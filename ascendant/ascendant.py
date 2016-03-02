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
    def __init__(self, num_required_to_fail, num_required_for_mission):

        # based on the round number and number of players
        self.num_required_to_fail = num_required_to_fail
        self.num_required_for_mission = num_required_for_mission

        # the number of proposals that have failed this round
        self.num_failed_proposals = 0

        # the players going on this rounds mission
        self.mission_members = []

        # vote dictionaries for proposing and missions
        self.proposal_votes = {}
        self.mission_votes = {}

        # not sure...? I think Joseph put this here
        self.stalled = 0

    def set_mission_members(self, member_list):
        # this shouldn't ever happen
        if len(member_list) != self.mission_members:
            raise AscendantError('Given num of players on mission: {}; should be {}'.format(
                len(member_list),
                self.num_on_mission)
            )

        self.mission_members = member_list

    def proposal_vote(self, pid, vote):
        self.proposal_votes[pid] = bool(vote)

    def mission_vote(self, pid, vote):
        if pid in self.players_on_mission:
            self.mission_votes[pid] = bool(vote)

    def do_proposal_vote(self):    
        passed = sum(1 if v else -1 for v in self.proposal_votes.values()) > 0

        if not passed:
            self.number_failed_proposals += 1

        votes = self.proposal_votes
        self.proposal_votes = {}

        return passed, votes

    def do_mission_vote(self):
        passed = sum(1 if v else -1 for v in self.mission_votes.values()) > 0
        return passed

    def to_dict(self):
        return {'num_failed_proposals': self.num_failed_proposals,
                'mission_members': self.mission_members,
                'proposal_votes': self.proposal_votes,
                'mission_votes': self.mission_votes
            }

# class that keeps track of the game state
class AscendantGame(object):

    @staticmethod
    def gen_id():
        return ''.join(random.choice(uppercase) for _ in range(4))

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

        self.rounds = []

        self.round_num = -1

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

    def all_voted_proposal(self):
        return len(self.rounds[-1].votes) >= len(self.players)

    def propose_mission(self, pids):
        rounds[-1].set_mission_members(pids)        

    def start_proposal(self):
        self.leader_index = (self.leader_index + 1) % len(self.players)
        self.state = GAMESTATE_PROPOSING
        self.rounds[-1].proposal_votes = {}

    def all_voted_mission(self):
        return len(self.current_round.mission_votes) >= self.current_round.num_on_mission

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

    def get_proposal_votes(self):
        return rounds[-1].do_proposal_vote()

    def get_mission_votes(self):    
        return rounds[-1].do_mission_vote()

    def mission_vote(self, pid, vote):
        self.rounds[-1].mission_vote(pid, vote)

    def get_player(self, pid):
        'much inefficient, very O(n)'
        for player in self.players:
            if player.player_id == pid:
                return player
        return None

    def remove_player(self, pid):
        if self.state == GAMESTATE_JOINING and self.get_player(pid) in self.players:
            self.players.remove(self.get_player(pid))
            return True
        return False

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

        self.state = GAMESTATE_READYING

    def start_round(self):

        self.round_num += 1

        # change to take into account round num and number of players
        self.rounds.append(GameRound(1, 3))

    def to_dict(self):
        return {'game_id': self.game_id,
                'creator': self.creator.to_dict(),
                'leader': self.get_leader().to_dict(),
                'players': [p.to_dict() for p in self.players],
                'rounds': [r.to_dict() for r in self.rounds]
            }
