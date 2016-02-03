# -*- coding: utf-8 -*-

"""
Settings
========

General/global settings file
"""

MAX_NUM_OF_PLAYERS = 10
MIN_NUM_OF_PLAYERS = 5

# custom exception
class AscendantError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)
