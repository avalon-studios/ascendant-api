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
from settings import *

# class that keeps track of the game state
class ascendant_game:

    # init file takes the user-friendly name and 
    # the uuid of the player who started the room
    def __init__(self, uuid_name, uf_name):
        # player_map maps uuid to user-friendly name
        self.player_map = dict()
        self.player_map[uuid_name] = uf_name         

        # number won by good team
        self.good_won = 0 

        # number won by bad team
        self.bad_won = 0  

        # number stalled (resets each round
        self.stalled = 0

        # list of good players
        self.good_players = []

        # list of bad playerss
        self.bad_players = []

    # returns true if the player can be added to the map,
    # returns false if the game is full
    #
    # look into seeing if this needs to have a thread lock
    def add_player(self, uuid_name, uf_name):
        if len(self.player_map) < MAX_NUM_OF_PLAYERS:
            self.player_map[uuid_name] = uf_name
            return True
        else:
            return False

    def is_ready_to_start(self):
        if len(self.player_map) >= MIN_NUM_OF_PLAYERS:
            return True
        else:
            return False

    # returns the number of players necessary to have 
    # enough, 0 if the game is ready to start
    def how_many_needed_to_start(self):
        x = MIN_NUM_OF_PLAYERS - len(self.player_map)
        return x if x > 0 else 0

    # function that will be called when user selects "start game"
    # allocates who is good and bad
    def start_game(self):
        # this should be called outside this function before 
        # the web handler calls this function, but just to make
        # sure
        if not self.is_ready_to_start():
            # yell at the developer who didn't check this
            return False

        shuffled_uuids = self.player_map.keys()
        random.shuffle(shuffled_uuids)

        # Essentially it is split up such that 2/3
        # of the players are good and 1/3 are bad
        self.good_players = shuffled_uuids[0:int(math.floor((2.0/3.0) * len(self.player_map)))]
        self.bad_players = shuffled_uuids[int(math.floor((2.0/3.0) * len(self.player_map))):]

        return True


    

    


