# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import ascendant.ascendant as ascendant 

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

# temporarily use dictionary to store stuffs
games = {}

def debug(msg):
    print(msg)

if __name__ == '__main__':
    socketio.run(app)

@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('create')
def on_create(data):
    
    # grab the info need to make a player
    creator_id = str(uuid.uuid4())
    name = data['name']

    # make a player and a game
    game_id = ascendant.AscendantGame.gen_id()
    creator = ascendant.Player(creator_id, name)
    game = ascendant.AscendantGame(game_id, creator)

    # save the game
    games[game_id] = game

    debug('game {} created'.format(game_id))
    # add the user to the game room
    join_room(game_id)

    # emit the creation back to the client
    return {'game_id': game_id, 'player': creator.to_dict()}

    #emit('create', {'game_id': game_id, 'player': {'id': creator.player_id, 'name': creator.name, 'team': creator.team}}, json=True)

@socketio.on('join')
def on_join(data):
    # get data needed for player
    game_id = str(data['game_id'])
    player_id = str(uuid.uuid4())
    name = data['name']

    # create the player and join the room
    player = Player(player_id, name)
    join_room(game_id)

    game = games[game_id]


    success = games[game_id].add_player(player)

    if success:
        socketio.emit('update_players',
            [p.to_dict() for p in game.players],
            room=game_id,
            json=True
        )

        return {
            'succes': True,
            'game_id': game_id,
            'player': player.to_dict(),
            'players': [p.to_dict() for p in game.players]
        }
    else:
        return {'succes': False, 'error_message': 'couldnt join the fuckin game'}

