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

class GameBackend(object):
    """Manages game state and provides interface for interacting with a game."""

    def __init__(self, channel):
        self.players = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(channel)

    def join(self, client):
        self.players.append(client)



@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/')
def receive(ws):
    while ws.socket is not None:

        gevent.sleep(0.1)
        received_string = ws.receive()

        received_json = None
        action = None
        game_room = None

        try:
            received_json = json.loads(received_string)
            action = received_json['action']
            room_id = received_json['room']
        except:
            print('Failed to parse action')
            continue

        if action == CREATE_ACTION:     
            create_room(ws)
        elif action == JOIN_ACTION:       
            join_game(ws, room_id)
        elif action == VOTE_ACTION:
            try:
                vote = received_json['vote']
                vote(ws, room_id, vote)
            except:
                print('Attemped to vote with no vote value')
        elif action == PROPOSE_MISSION_ACTION:


def create_room(client):
    new_id = room_id_generator()

    while games[new_id] is not None:
        new_id = room_id_generator()

    new_game = GameBackend()
    new_game.join(client)

    games[new_id] = new_game

def join_game(client, room_id):
    try:
        game = games[room_id]
        game.join(client)
    except:
        print('Game does not seem to exist')

def vote(client, room_id, vote):
    try:
        game = games[room_id]
        game.vote()
    except:
        print('Game does not seem to exist')
        
def room_id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(4))

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



