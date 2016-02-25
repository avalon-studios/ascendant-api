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
from flask_socketio import SocketIO, send, emit

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

if __name__ == '__main__':
    socketio.run(app)

def room_id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(4))

@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('create')
def create(json):
    jsonString = '{"game_id": "asdf", "player": {"id": "abc","name": "Kyle","team": 0}}'
    emit('create', jsonString, json=True)

# class to house the backend and websocket interface
class GameInterface(object):
    """Game backend class"""

    def start(self):
        socketio.run(app)

    @socketio.on('json')
    def handle_json(self, json):
        send(json, json=True)

