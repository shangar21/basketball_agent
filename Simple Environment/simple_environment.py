import numpy as np
from player import SimplePlayer, DistanceBucket, Attempt
from enum import Enum

'''
STATE = [
    attacking player field goal restricted area percentage,
    .
    .
    .
    attacking player free throw percentage,
    attacking player offensive rebounds percentage,
    attacking player assist percentage,
    attacking player turn over percentage,
    .
    .
    .
    defending player steal percentage,
    defending player block percentage,
    defending player personal fouls percentage,
    defending player defensive rebounds percentage,
    attacking player distance from net
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
    SHOOT = 2
    DRIBBLE_FORWARD = -1
    DRIBBLE_BACK = 1
    PASS = 3

class SimpleBasketball():
    def __generate_state(self):
        attack_keys = ['ftp', 'orebp', 'astp', 'tovp']
        defend_keys = ['stlp', 'blkp', 'pfp', 'drebp']
        player_with_ball = self.attack_players[self.attack_player]
        defending_player = self.defend_players[self.attack_player]
        attack_fgp = [player_with_ball.fgp[k] for k in DistanceBucket]
        attack_stats = [getattr(player_with_ball, k) for k in attack_keys]
        defend_stats = [getattr(defending_player, k) for k in defend_keys]
        return attack_fgp + attack_stats + defend_stats + [player_with_ball.distance.value]

    def __init__(self, attack_players, defend_players, player_with_ball=None):
        self.attack_players = attack_players
        self.defend_players = defend_players
        self.attack_player = np.random.choice(list(self.attack_players.keys())) if not player_with_ball else player_with_ball
        self.state = self.__generate_state()
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
                self.reward = 2 if self.attack_players[self.attack_player].distance.value <= DistanceBucket.MIDRANGE.value else 3
                self._shoot_ft(num_shots=1, and_one=True)
            else:
                self._shoot_ft()
        elif shot_made is Attempt.SUCCESS:
            if self.attack_players[self.attack_player].distance.value >= DistanceBucket.LEFT_CORNER_THREE.value:
                print(f'Player {self.attack_players[self.attack_player].name} makes three point shot.')
                self.reward = 3
            elif self.attack_players[self.attack_player].distance.value <= DistanceBucket.MIDRANGE.value:
                print(f'Player {self.attack_players[self.attack_player].name} makes two point shot.')
                self.reward = 2
        elif shot_made is Attempt.FAIL:
            print(f'Player {self.attack_players[self.attack_player].name} misses shot.')
            self.reward = -2
        return shot_made, shot_blocked

    def _find_player_in_paint(self):
        for i in self.attack_players:
            if self.attack_players[i].distance.value <= DistanceBucket.IN_THE_PAINT.value:
                return i

    def _rebound(self):
        player_in_paint = self._find_player_in_paint()
        if player_in_paint:
            rebound_attempt = self.attack_players[player_in_paint].offensive_rebound()
            d_rebound_attempt = self.defend_players[player_in_paint].defensive_rebound()
            if rebound_attempt is Attempt.SUCCESS and d_rebound_attempt is Attempt.FAIL:
                print(f'Shot Missed, player {self.attack_players[player_in_paint].name} got rebound!')
                self.reward += 2
                return player_in_paint
            elif rebound_attempt is Attempt.SUCCESS and d_rebound_attempt is Attempt.SUCCESS:
                print(f'Shot missed,  player {self.defend_players[player_in_paint].name} got defensive rebound')
            else:
                print(f'Shot Missed, player {self.attack_players[player_in_paint].name} went for rebound, but did not get it!')

    def _dribble(self, direction):
        new_dist = DistanceBucket(self.attack_players[self.attack_player].distance.value + direction)
        print(f'Player {self.attack_players[self.attack_player].name} is dribbling to {new_dist} from {self.attack_players[self.attack_player].distance}')
        defensive_steal = self.defend_players[self.attack_player].steal()
        if defensive_steal is Attempt.FOUL:
            print(f'Player {self.defend_players[self.attack_player].name} fouls, freethrow rewarded')
            self._shoot_ft()
        elif defensive_steal is Attempt.SUCCESS:
            print(f'Player {self.defend_players[self.attack_player].name} steals ball!')
            self.reward -= 2
        else:
            print(f'Player {self.attack_players[self.attack_player].name} makes it to {new_dist}')
            self.reward += 1
        return defensive_steal, new_dist


    def step(self, action):
        self.reward = 0
        print(f'Player {self.attack_players[self.attack_player].name} has ball.')
        if action is Action.SHOOT:
            shot_made, shot_blocked = self._shoot_fg()
            if shot_made is Attempt.FAIL and shot_blocked is Attempt.FAIL:
                current_possession = self._rebound()
                if current_possession:
                    self.attack_player = current_possession
                    self.__generate_state()
                else:
                    self.is_in_play = False
            else:
                self.is_in_play = False
            return self.reward
        elif action is Action.DRIBBLE_FORWARD:
            if self.attack_players[self.attack_player].distance.value > 0:
                defensive_steal, new_dist = self._dribble(action.value)
                if defensive_steal is Attempt.FAIL:
                    self.attack_players[self.attack_player].distance = new_dist
                    self.__generate_state()
                else:
                    self.is_in_play = False
            else:
                    self.step(Action.DRIBBLE_BACK)
        elif action is Action.DRIBBLE_BACK:
            if self.attack_players[self.attack_player].distance.value < 4:
                defensive_steal, new_dist = self._dribble(action.value)
                if defensive_steal is Attempt.FAIL:
                    self.attack_players[self.attack_player].distance = new_dist
                    self.__generate_state()
                else:
                    self.is_in_play = False
            else:
                    self.step(Action.DRIBBLE_FORWARD)
