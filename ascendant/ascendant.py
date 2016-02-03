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

# local libraries

# constants are defined in settings, also holds AscendantError
from settings import *

class Player(object):
    """Game player class"""

    def __init__(self, player_id, real_name):
        self.player_id = player_id
        self.real_name = real_name
        self.team = -1

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
            raise AscendantError('Given num of players on mission: {}; should be {}'.format(len(member_list), self.num_on_mission))

            

    def vote(self, passfail):
        if passfail:
            self.num_passes += 1
        else:
            self.num_fails += 1



# class that keeps track of the game state
class AscendantGame(object):

    # init file takes the game_id and Player that is
    # the creator
    def __init__(self, game_id, creator):
        self.game_id = game_id

        # player list
        self. player_list = [creator]
        
        # keep track of creator
        self.creator = creator

        # number won by good team
        self.good_won = 0 

        # number won by bad team
        self.bad_won = 0  

        # list of good players
        self.good_players = []

        # list of bad playerss
        self.bad_players = []

    # returns true if the player can be added to the map,
    # returns false if the game is full
    #
    # look into seeing if this needs to have a thread lock
    def add_player(self, uuid_name, uf_name):
        if len(self.player_list) < MAX_NUM_OF_PLAYERS:
            player_list
            return True
        else:
            return False

    def is_ready_to_start(self):
        if len(self.player_list) >= MIN_NUM_OF_PLAYERS:
            return True
        else:
            return False

    # returns the number of players necessary to have 
    # enough, 0 if the game is ready to start
    def how_many_needed_to_start(self):
        x = MIN_NUM_OF_PLAYERS - len(self.player_list)
        return x if x > 0 else 0

    # function that will be called when user selects "start game"
    # allocates who is good and bad
    #
    # raises an exception if it doesn't work, else returns
    # list of good players, list of bad players
    def start_game(self):
        # this should be called outside this function before 
        # the web handler calls this function, but just to make
        # sure
        if not self.is_ready_to_start():
            # yell at the developer who didn't check this
            raise AscendantError("Not Enough Players")

        shuffled_uuids = self.player_list[:]
        random.shuffle(shuffled_uuids)

        # Essentially it is split up such that 2/3
        # of the players are good and 1/3 are bad
        self.good_players = shuffled_uuids[0:int(math.floor((2.0/3.0) * len(self.player_list)))]
        self.bad_players = shuffled_uuids[int(math.floor((2.0/3.0) * len(self.player_list))):]

        return self.good_players, self.bad_players

    

    

    


