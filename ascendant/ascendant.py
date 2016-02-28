# -*- coding: utf-8 -*-

"""
Game Logic
==========

This contains all the code used for running the game. This doesn't handle any of the web interfaces.

This particular library assumes that all the data necessary for each function to run has been collected, which means that all networking, waiting for data, etc. is handled elsewhere.
"""
# python libraries
import random
import math
from string import ascii_uppercase as uppercase

# local libraries

# constants are defined in settings, also holds AscendantError
from settings import *
from errors import *

class Player(object):
    """Game player class"""

    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.team = TEAM_NONE
        self.ready = False

    def to_dict(self, show_team=False):
        return {'id': self.player_id, 'name': self.name, 'team': self.team if show_team else -1}

class GameRound(object):
    def __init__(self, num_required_to_fail, num_on_mission):
        self.num_required_to_fail = num_required_to_fail
        self.num_on_mission = num_on_mission

        self.stalled = 0
        self.players_on_mission = []

        self.num_passes = 0
        self.num_fails = 0

    def set_mission_members(self, member_list):
        # this shouldn't ever happen
        if len(member_list) != self.num_on_mission:
            raise AscendantError('Given num of players on mission: {}; should be {}'.format(
                len(member_list),
                self.num_on_mission)
            )

        self.players_on_mission = member_list

    def vote(self, passfail):
        if passfail:
            self.num_passes += 1
        else:
            self.num_fails += 1



# class that keeps track of the game state
class AscendantGame(object):

    @staticmethod
    def gen_id():
        return ''.join(random.choice(uppercase) for _ in range(50))

    # init file takes the game_id and Player that is
    # the creator
    def __init__(self, game_id, creator):
        self.game_id = game_id

        self.state = GAMESTATE_JOINING

        # player list
        self.players = [creator]
        self.leader_index = -1
        
        # keep track of creator
        self.creator = creator

        # number won by good team
        self.good_won = 0 

        # number won by bad team
        self.bad_won = 0  

        self.round_num = -1
        self.current_round = None


    '''
    returns true if the player can be added to the map,
    returns false if the game is full
   
    look into seeing if this needs to have a thread lock
    '''
    def add_player(self, player):
        if len(self.players) < MAX_NUM_OF_PLAYERS:
            self.players.append(player)
            return True
        else:
            return False

    def start_round(self):
        self.round_num += 1
        self.leader_index = (self.leader_index + 1) % len(self.players)

        self.current_round = GameRound(1, 3)

    def is_ready_to_start(self):
        return self.how_many_needed_to_start() == 0

    def how_many_needed_to_start(self):
        '''
        return the number of players necessary to have 
        enough, 0 if the game is ready to start
        '''
        return max(MIN_NUM_OF_PLAYERS - len(self.players), 0)

    def all_ready(self):
        return all(p.ready for p in self.players)

    def get_player(self, pid):
        'much inefficient, very O(n)'
        for player in self.players:
            if player.player_id == pid:
                return player
        return None

    def get_leader(self):
        return self.players[self.leader_index]

    def start_game(self):
        '''
        start a game and assign teams
        '''
        # this should be called outside this function before 
        # the web handler calls this function, but just to make
        # sure
        if not self.is_ready_to_start():
            # yell at the developer who didn't check this
            raise AscendantError("Not Enough Players")

        shuffled_players = self.players[:]
        random.shuffle(shuffled_players)

        # Essentially it is split up such that 2/3
        # of the players are good and 1/3 are bad
        n_good = int(2.0/3.0 * len(self.players))

        for player in shuffled_players[0:n_good]:
            player.team = TEAM_GOOD
        for player in shuffled_players[n_good:]:
            player.team = TEAM_BAD

        self.state = GAMESTATE_STARTED

