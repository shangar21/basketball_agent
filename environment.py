import numpy as np
from player import Player, DistanceBucket, Attempt
from enum import Enum

'''
STATE = [
    attacking pg field goal restricted area percentage,
    .
    .
    .
    attacking pg three point percentage,
    attacking pg free throw percentage,
    attacking pg offensive rebounds percentage,
    attacking pg assist percentage,
    attacking pg turn over percentage,
    .
    .
    .
    attacking center restricted area field goal percentage,
    .
    .
    .
    attacking center free throw percentage,
    attacking center offensive rebounds percentage,
    attacking center assist percentage,
    attacking center turn over percentage,
    defending pg steal percentage,
    defending pg block percentage,
    defending pg personal fouls percentage,
    defending pg defensive rebounds percentage,
    .
    .
    .
    defending center steal percentage,
    defending center block percentage,
    defending center personal fouls percentage,
    defending center defensive rebounds percentage,
    attacking center distance from net,
    .
    .
    .
    attacking center distance from net,
    defending pg distance from net,
    player with ball,
]
'''

'''
attack_players = {
    'pg': Player,
    'sg': Player,
    'sf': Player,
    'pf': Player,
    'c': Player,
}
'''

class Action(Enum):
    SHOOT = 1
    DRIBBLE = 0
    PASS = 1

class Basketball():
    def __unpack(self, attribute, key):
        distance_bucket_order = [DistanceBucket.RESTRICTED_AREA, DistanceBucket.IN_THE_PAINT, DistanceBucket.MIDRANGE, DistanceBucket.LEFT_CORNER_THREE, DistanceBucket.RIGHT_CORNER_THREE, DistanceBucket.ABOVE_THE_BREAK_THREE]
        if key == 'fgp':
            return [i for i in [attribute[k] for k in distance_bucket_order]]
        return [attribute]

    def __generate_state(self, attack_players, defend_players):
        player_order = ['pg', 'sg', 'sf', 'pf', 'c']
        attack_keys = ['fgp', 'ftp', 'orebp', 'astp', 'tovp']
        defend_keys = ['stlp', 'blkp', 'pfp', 'drebp']

        attack_state = []

        for i in [attack_players[key] for key in player_order]:
            for k in attack_keys:
                attack_state += self.__unpack(getattr(i, k), k)

        return attack_state +\
            [getattr(defend_player, k) for k in defend_keys for defend_player in [defend_players[key] for key in player_order]] +\
             [attack_player.distance for attack_player in [attack_players[key] for key in player_order]] +\
                [self.attack_player]

    def __init__(self, attack_players, defend_players, player_with_ball=None):
        self.attack_players = attack_players
        self.defend_players = defend_players
        self.attack_player = np.random.choice(list(self.attack_players.keys())) if not player_with_ball else player_with_ball
        self.state = self.__generate_state(attack_players, defend_players)
        self.is_in_play = True
        self.reward = 0

    def _shoot_ft(self, num_shots = 2, and_one=False):
        pts = 0
        for i in range(num_shots):
            if self.attack_players[self.attack_player].free_throw() == Attempt.SUCCESS:
                pts += 1
                print(f'Freethrow made.')
            else:
                pts -= 1 if not and_one else 0
                print(f'Missed freethrow.')
        self.reward += pts

    def _shoot_fg(self):
        print(f'Player {self.attack_players[self.attack_player].name} shoots ball from {self.attack_players[self.attack_player].distance}')
        shot_made = self.attack_players[self.attack_player].field_goal()
        shot_blocked = self.defend_players[self.attack_player].block()
        if shot_blocked is Attempt.SUCCESS:
            print(f'Player {self.defend_players[self.attack_player].name} blocks shot.')
            self.reward = -2
        elif shot_blocked is Attempt.FOUL:
            print(f'Player {self.attack_players[self.attack_player].name} was fouled.')
            if shot_made is Attempt.SUCCESS:
                print(f'Shot made, and 1 granted.')
                self.reward = 2 if distance.value <= DistanceBucket.MIDRANGE.value else 3
                self._shoot_ft(num_shots=1, and_one=True)
            else:
                self._shoot_ft()
        elif shot_made is Attempt.SUCCESS:
            if distance.value >= DistanceBucket.LEFT_CORNER_THREE.value:
                print(f'Player {self.attack_players[self.attack_player].name} makes three point shot.')
                self.reward = 3
            elif distance.value <= DistanceBucket.MIDRANGE.value:
                print(f'Player {self.attack_players[self.attack_player].name} makes two point shot.')
                self.reward = 2
        elif shot_made is Attempt.FAIL:
            print(f'Player {self.attack_players[self.attack_player].name} misses shot.')
            self.reward = -2
        return shot_made, shot_blocked

    def _rebound(self):
        pass

    def step(self, action):
        print(f'Player {self.attack_players[self.attack_player].name} has ball.')
        if action == Action.SHOOT:
            shot_made, shot_blocked = self._shoot_fg()
            print(f'Reward for this epiode is {self.reward}')
            if shot_made is Attempt.FAIL and shot_blocked is Attempt.FAIL:
                self._rebound()
            return self.reward


