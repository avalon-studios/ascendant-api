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

# dictionary of the current game objects -- there is probably a better way to do this,
# but for now this is the easiest.
current_games = {}

if __name__ == '__main__':
    socketio.run(app)

def room_id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(4))

@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('create')
def on_create(data):
    
@socketio.on('join')
def on_join(data):
    player_id = data['id']

# class to house the backend and websocket interface
class GameInterface(object):
    """Game backend class"""

    players = []

    def __init__(self, game_id, creator):
        self.game_id = game_id
        self.creator = creator
        self.players.append(creator)

    def update_players():
        socketio.send(players, json=True, room=game_id)

class Player(object):
    """Game player class"""

    def __init__(self, id, name):
        self.id = id
        self.name = name
