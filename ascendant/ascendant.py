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
        
        self.acks = {
            'do_proposal_vote': False,
            'mission_vote_result': False,
            'proposal_vote_result': False,
            'update_players': False,
            'assign_roles': False,
            'propose_mission': False
        }

    def to_dict(self, show_team=False):
        return {'id': self.player_id, 'name': self.name, 'team': self.team if show_team else -1}

class GameRound(object):
    def __init__(self, num_required_to_fail, num_on_mission):
        self.num_required_to_fail = num_required_to_fail
        self.num_on_mission = num_on_mission

        self.stalled = 0
        self.players_on_mission = []
        self.votes = {}
        self.mission_votes = {}
        # starts at -1 since each start_proposal call 
        # increments it by 1
        self.number_failed_proposals = -1

    def set_mission_members(self, member_list):
        # this shouldn't ever happen
        if len(member_list) != self.num_on_mission:
            raise AscendantError('Given num of players on mission: {}; should be {}'.format(
                len(member_list),
                self.num_on_mission)
            )

        self.players_on_mission = member_list

    def vote(self, pid, vote):
        self.votes[pid] = bool(vote)

    def mission_vote(self, pid, vote):
        if pid in self.players_on_mission:
            self.mission_votes[pid] = bool(vote)


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

        # number won by good team
        self.good_won = 0

        # number won by bad team
        self.bad_won = 0

        self.round_passes = []

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

    def all_voted(self):
        return len(self.current_round.votes) >= len(self.players)

    def start_round(self):
        # safe the round pass/fail so we can send when someone rejoins
        if self.current_round:
            self.round_passes.append(self.get_mission_votes())

        n_players = len(self.players)
        self.round_num += 1
        to_send = {
            5: [2, 3, 2, 3, 3],
            6: [2, 3, 3, 3, 4],
            7: [2, 3, 3, 4, 4],
            8: [3, 4, 4, 5, 5],
            9: [3, 4, 4, 5, 5],
            10: [3, 4, 4, 5, 5]
        }
        to_fail = {
            5: [1, 1, 1, 1, 1],
            6: [1, 1, 1, 1, 1],
            7: [1, 1, 1, 2, 1],
            8: [1, 1, 1, 2, 1],
            9: [1, 1, 1, 2, 1],
            10: [1, 1, 1, 2, 1],
        }
        self.current_round = GameRound(to_fail[n_players][self.round_num], to_send[n_players][self.round_num])

    def start_proposal(self):
        self.current_round.number_failed_proposals += 1
        self.leader_index = (self.leader_index + 1) % len(self.players)
        self.state = GAMESTATE_PROPOSING
        self.current_round.votes = {}

    def start_mission_voting(self):
        self.state = GAMESTATE_MISSION_VOTE
        self.current_round.mission_votes = {}

    def all_mission_voted(self):
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
    
    def all_seen_votes(self):
        return all(p.seen_vote for p in self.players)

    def get_votes(self):    
        passed = sum(1 if v else -1 for v in self.current_round.votes.values()) > 0

        if not passed:
            self.current_round.number_failed_proposals += 1
        else:
            self.current_round.number_failed_proposals = 0

        return passed, self.current_round.votes

    def get_mission_votes(self):    
        fail_votes = len([v for v in self.current_round.mission_votes.values() if not v])
        # returns true if it passes
        if not (fail_votes >= self.current_round.num_required_to_fail):
            self.good_won += 1;
            return True
        else:
            self.bad_won += 1;
            return False

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

    def get_failed_proposals(self):
        if self.current_round:
            return self.current_round.number_failed_proposals
        return 0

    def get_current_state(self):
        return self.state

    def set_mission_members(self, pids):
        self.state = GAMESTATE_PROPOSAL_VOTE
        self.current_round.set_mission_members(pids)

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

    def is_over(self):
        if self.good_won == NUM_WINS or self.bad_won == NUM_WINS:
            return True
        elif self.current_round.number_failed_proposals == MAX_NUM_ROUND_FAILS:
            return True
        else:
            return False

    def all_acks_received(self, ack_type):
        for player in game.players:
            if (player.acks[ack_type] == False)
                    return False
        return True

