# -*- coding: utf-8 -*-

"""
Errors
======

General/Specific Exceptions
"""

class AscendantError(Exception):
    '''
    General Exception
    '''
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)

class NotEnoughPlayers(AscendantError):
    '''
    Error for not enough players in the room
    '''
    def __init__(self, description):
        AscendantError.__init__(self, description)


