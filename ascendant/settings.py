# -*- coding: utf-8 -*-

"""
Settings
========

General/global settings file
"""

TEAM_NONE = -1
TEAM_GOOD = 0
TEAM_BAD = 1

MAX_NUM_OF_PLAYERS = 10
MIN_NUM_OF_PLAYERS = 5

GAMESTATE_JOINING = 0
GAMESTATE_STARTED = 1

# custom exception
class AscendantError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)
