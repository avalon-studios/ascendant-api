# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import redis
import gevent
import json
import random
from flask import Flask, render_template
from flask_sockets import Sockets

REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'chat'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)

CREATE_ACTION           = 'create'
JOIN_ACTION             = 'join'
# Same action for proposals and mission failures? or different ones to be safe?
VOTE_ACTION             = 'vote'
PROPOSE_MISSION_ACTION  = 'propose'



class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

chats = ChatBackend()
chats.start()

games = {}

def create_room(client):
    new_id = room_id_generator()

    while games[new_id] is not None:
        new_id = room_id_generator()

    new_game = GameBackend(new_id)
    new_game.join(client)

    games[new_id] = new_game

def room_id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(4))

class GameBackend(object):
    """Manages game state and provides interface for interacting with a game."""

    def __init__(self, channel):
        self.players = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(channel)

    def join(self, player):
        self.players.append(player)

    def vote(self, player, action_json):
        print('vote')

    def propose_mission(self, player, action_json):
        print('propose')

    def parse_action(self, action_json, player):
        
        action = action_json['action']

        if action == JOIN_ACTION:       
            self.join(player)
        elif action == VOTE_ACTION:
            self.vote(player, action_json)
        elif action == PROPOSE_MISSION_ACTION:
            self.propose_mission(player, action_json)


@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/game')
def receive(ws):
    while ws.socket is not None:

        gevent.sleep(0.1)
        received_string = ws.receive()

        received_json = None
        game = None

        try:
            received_json = json.loads(received_string)
            room_id = received_json['room']
            game = games[room_id]
        except:
            # probably make a room here? game = create_room(ws)?
            print('Invalid room, game does not seem to exist')
            continue

        game.parse_action(received_json)




@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while ws.socket is not None:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        print(message)

        try:
            message_json = json.loads(message)
            print('Loaded message as json')
            print(type(message_json))
            print(message_json)
            print(message_json['action'])
        except:
            print('Failed to parse message as json')

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while ws.socket is not None:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()



