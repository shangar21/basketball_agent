import numpy as np
from player import Player

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

class Basketball():
    def __generate_state(self, attack_player, defend_player, distance_from_net):
        attack_keys = ['fgp', 'tpp', 'ftp', 'orebp', 'ast', 'tov']
        defend_keys = ['stlp', 'blkp', 'pfp', 'drebp']

        return [getattr(attack_player, k) for k in attack_keys] + [getattr(defend_player, k) for k in defend_keys] + [distance_from_net]

    def __init__(self, attack_player, defend_player, distance_from_net):
        self.attack_player = attack_player
        self.defend_player = defend_player
        self.distance_from_net = distance_from_net
        self.state = self.__generate_state(attack_player, defend_player, distance_from_net)
        self.is_in_play = True
        self.reward = 0

    def step(self, action):
        pass
