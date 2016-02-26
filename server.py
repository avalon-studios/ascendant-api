# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import json
import random
import uuid
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room

# set up Redis environment for use with heroku
REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'game'

# set up flask/socketio environment
app = Flask(__name__)
socketio = SocketIO(app, message_queue=REDIS_URL, channel=REDIS_CHAN)

CREATE_ACTION           = 'create'
JOIN_ACTION             = 'join'
# Same action for proposals and mission failures? or different ones to be safe?
VOTE_ACTION             = 'vote'
PROPOSE_MISSION_ACTION  = 'propose'

games = {}

if __name__ == '__main__':
    socketio.run(app)

def game_id_generator():
    
    return 'ASDF'

    # return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(4))

@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('create')
def on_create(data):
    
    # grab the info need to make a player
    game_id = game_id_generator()
    creator_id = str(uuid.uuid4())
    name = data['name']

    # make a player and a game
    creator = Player(creator_id, name)
    game = Game(game_id, creator)

    # save the game
    games[game_id] = game

    # add the user to the game room
    join_room(game_id)

    # return the creation back to the client
    return {'game_id': game_id, 'player': {'id': creator.id, 'name': creator.name, 'team': creator.team}}

@socketio.on('join')
def on_join(data):

    # get data needed for player
    game_id = str(data['game_id'])
    player_id = str(uuid.uuid4())
    name = data['name']

    # create the player and join the room
    player = Player(player_id, name)
    join_room(game_id)

    games[game_id].add_player(player)

    return {'game_id': game_id, 'player': {'id': player.id, 'name': player.name, 'team': player.team}, 'players': games[game_id].json_players}


# class to house the backend and websocket interface
class Game(object):
    """Game backend class"""

    def __init__(self, game_id, creator):
        self.game_id = game_id
        self.creator = creator
        self.players = [creator]
        self.json_players = []


    def add_player(self, player):
        self.players.append(player)
        self.update_players()

    def update_players(self):

        for player in self.players:
            self.json_players.append({'id': player.id, 'name': player.name, 'team': player.team})

        socketio.emit('update_players', self.json_players, json=True, room=self.game_id)

class Player(object):
    """Game player class"""

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.team = 0




