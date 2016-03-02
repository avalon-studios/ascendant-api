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

from ascendant.settings import *

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


@socketio.on('propose_mission')
def on_propose(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']
    player_ids = data['player_ids']

    game = games[game_id]
    player = game.get_player(player_id)

    if player_id != game.get_leader().player_id:
        return {'success': False, 'error_message': 'u r no leader'}

    if len(player_ids) != game.current_round.num_on_mission:
        return {'success': False, 'error_message': 'bad number of players'}

    game.current_round.set_mission_members(player_ids)

    socketio.emit('do_proposal_vote', 
        {'players': player_ids},
        json=True,
        room=game_id,
    )
        
    return {'success': True}


@socketio.on('mission_vote')
def on_mission_vote(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']
    vote = data['vote']

    game = games[game_id]

    game.current_round.mission_vote(player_id, vote)

    debug('{}'.format(game.all_mission_voted()))

    if game.all_mission_voted():
        passed = game.get_mission_votes()
        debug('errbody voted on mission. passed: {}'.format(passed))
        socketio.emit('mission_vote_result', 
            {
                'pass': passed,
                'mission_number': game.round_num
            },
            json=True,
            room=game_id,
        )

        # start the next round
        game.start_round()
        game.start_proposal()
        socketio.emit('propose_mission',
            {
                'leader': game.get_leader().to_dict(),
                'mission_number': game.round_num,
                'number_players': game.current_round.num_on_mission,
            },
            json=True,
            room=game_id,
        )

    return {'success': True}

@socketio.on('proposal_vote')
def on_vote(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']
    vote = data['vote']

    game = games[game_id]
    player = game.get_player(player_id)


    game.current_round.vote(player_id, vote)

    debug('player {} voted {}'.format(player_id, vote))
    if game.all_voted():
        passed, votes = game.get_votes()
        debug('errybody voted on proposal. passed: {}'.format(passed))
        socketio.emit('proposal_vote_result',
            {
                'pass': passed,
                'votes': votes,
                'players': game.current_round.players_on_mission
            },
            json=True,
            room=game_id,
        )

        if not passed:
            # redo the proposal
            game.start_proposal()
            socketio.emit('propose_mission',
                {
                    'leader': game.get_leader().to_dict(),
                    'mission_number': game.round_num,
                    'number_players': game.current_round.num_on_mission,
                },
                json=True,
                room=game_id,
            )
        else:
            game.start_mission_voting()

    return {'success': True}


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
    join_room(creator.player_id)

    # emit the creation back to the client
    return {'game_id': game_id, 'player': creator.to_dict()}


@socketio.on('join')
def on_join(data):
    # get data needed for player
    game_id = str(data['game_id'])
    player_id = str(uuid.uuid4())
    name = data['name']

    # create the player and join the room
    player = ascendant.Player(player_id, name)
    join_room(game_id)
    join_room(player_id)

    debug(games)
    game = games[game_id]

    success = games[game_id].add_player(player)

    debug('joining game. success: {}'.format(success))

    if success:
        socketio.emit('update_players',
            [p.to_dict() for p in game.players],
            room=game_id,
            json=True
        )

        return {
            'success': True,
            'game_id': game_id,
            'player': player.to_dict()
        }
    else:
        return {'success': False, 'error_message': 'Unable to join game'}


@socketio.on('start')
def on_start(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']

    # create the player and join the room
    game = games[game_id]
    player = game.get_player(player_id)

    if not game.is_ready_to_start():
        return {'success': False, 'error_message': 'You need at least five players to start'}

    game.start_game()

    for player in game.players:
        socketio.emit('assign_roles',
            {
                'player': player.to_dict(show_team=True),
                'players': [p.to_dict(show_team=player.team==TEAM_BAD) for p in game.players],
            },
            json=True,
            room=player.player_id,
        )
            

    return {'success': True}


@socketio.on('ready')
def on_ready(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']

    # create the player and join the room
    game = games[game_id]
    player = game.get_player(player_id)

    debug('player {} is ready'.format(player.player_id))
    player.ready = True

    if game.all_ready():
        debug('errybody ready')
        game.start_round()
        game.start_proposal()
        socketio.emit('propose_mission',
            {
                'leader': game.get_leader().to_dict(),
                'mission_number': game.round_num,
                'number_players': game.current_round.num_on_mission,
            },
            json=True,
            room=game_id,
        )

    return {'success': True}


@socketio.on('leave')
def on_leave(data):
    # get data needed for player
    game_id = data['game_id']
    player_id = data['player_id']

    game = games[game_id]

    success = game.remove_player(player_id)

    debug('leaving game. success: {}'.format(success))

    if success:
        socketio.emit('update_players',
                [p.to_dict() for p in game.players],
                room=game_id,
                json=True
            )

    return {'success': success}



