import numpy as np
from player import Player, DistanceBucket, Attempt
from enum import Enum

'''
STATE = [
    attacking player field goal percentage,
    attacking player three point percentage,
    attacking player free throw percentage,
    attacking player offensive rebounds percentage,
    attacking player assist percentage,
    attacking player turn over percentage,
    defending player steal percentage,
    defending player block percentage,
    defending player personal foul percentage,
    defending player defensive rebound percentage,
    distance from net
]
'''

class Action(Enum):
    SHOOT = 1
    DRIBBLE = 0
    PASS = 1

class Basketball():
    def __generate_state(self, attack_player, defend_player, distance_from_net):
        attack_keys = ['fgp', 'ftp', 'orebp', 'astp', 'tovp']
        defend_keys = ['stlp', 'blkp', 'pfp', 'drebp']

        return [getattr(attack_player, k) for k in attack_keys] + [getattr(defend_player, k) for k in defend_keys] + [distance_from_net]

    def __init__(self, attack_player, defend_player, distance_from_net):
        self.attack_player = attack_player
        self.defend_player = defend_player
        self.distance_from_net = distance_from_net
        self.state = self.__generate_state(attack_player, defend_player, distance_from_net)
        self.is_in_play = True
        self.reward = 0

    def _shoot_ft(self, num_shots = 2):
        pts = 0
        for i in range(num_shots):
            if self.attack_player.free_throw() == Attempt.SUCCESS:
                pts += 1
                print(f'Freethrow made.')
            else:
                pts -= 1
                print(f'Missed freethrow.')
        self.reward += pts

    def _shoot_fg(self):
        distance = self.state[-1]
        print(f'Player {self.attack_player.name} shoots ball from {distance}')
        shot_made = self.attack_player.field_goal(distance)
        shot_blocked = self.defend_player.block()
        if shot_blocked is Attempt.SUCCESS:
            print(f'Player {self.defend_player.name} blocks shot.')
            self.reward = -2
        elif shot_blocked is Attempt.FOUL:
            if shot_made is Attempt.SUCCESS:
                print(f'Player {self.attack_player.name} was fouled, and made shot. And 1 granted.')
                self.reward += 2 if distance.value <= DistanceBucket.MIDRANGE.value else 3
                self._shoot_ft(num_shots=1)
            else:
                print(f'Player {self.attack_player.name} was fouled. Shooting free throw.')
                self._shoot_ft()
        elif shot_made is Attempt.SUCCESS and distance.value >= DistanceBucket.LEFT_CORNER_THREE.value:
            print(f'Player {self.attack_player.name} makes three point shot.')
            self.reward = 3
        elif shot_made is Attempt.SUCCESS and distance.value <= DistanceBucket.MIDRANGE.value:
            print(f'Player {self.attack_player.name} makes two point shot.')
            self.reward = 2
        elif shot_made is Attempt.FAIL:
            print(f'Player {self.attack_player.name} misses shot.')
            self.reward = -2

    def step(self, action):
        if action == Action.SHOOT:
            self._shoot_fg()
            print(f'Reward for this epiode is {self.reward}')
            return self.reward

