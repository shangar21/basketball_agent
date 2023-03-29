from attack_player import AttackPlayer
from defend_player import DefendPlayer
from shooting_manager import ShotManager
from dribbling_manager import DribbleManager
from rebound_manager import ReboundManager
from pass_manager import PassManager
from assets import court, assets
import pandas as pd
import numpy as np
import shapely
import geopandas as gpd
from shapely.geometry import Point
import random

class BasketballEnvironment():

    PLAYER_STARTING_POSITIONS = {
        'PG': (0, 30),
        'SG': (16,22),
        'SF': (-24, 5),
        'PF': (-10, 18),
        'C': (10, 3)
    }

    def __init__(self, dataset_path='./assets/datasets/'):
        self.path = dataset_path
        self.court, self.whole_court = court.initialize_court('./assets/court.geojson')
        self.attack_players = []
        self.defend_players = []
        self.shooting_managers = {}
        self.passing_managers = {}
        self.dribble_managers = {}
        self.rebound_managers = {}
        self.player_region = {
            'PG': self.court[self.court['name'] == 'three_point_range'],
            'SG': self.court[self.court['name'] == 'three_point_range'],
            'SF': self.court[self.court['name'] == 'midrange'],
            'PF': self.court[self.court['name'] == 'midrange'],
            'C':  self.court[self.court['name'] == 'midrange'],
        }

    def start(self):
        self.time = 24
        self.initialize_offensive_players()
        self.initialize_defensive_players()
        self.initialize_managers()
        self.player_with_ball = random.sample(self.attack_players, 1)[0]#self._find_player(self.attack_players, 'PG')
        self.is_in_play = True
        state = self.get_state()
        return self.get_state()

    def is_at_three(self, player):
        distance_bucket = court.point_to_region(player.position, self.court)
        return 'THREE' in distance_bucket.__str__()

    def distance_to_net(self, player):
        return np.sqrt(player.position[0]**2 + player.position[1]**2)

    def get_all_team_positions(self):
        positions = []
        for i in self.attack_players:
            for j in i.position:
                positions.append(j)
        return positions

    def get_pass_cols(self):
        cols = []
        for i in range(1, 12):
            for j in range(1, 12):
                if j == i:
                    continue
                cols.append(f'pass_box_{i}_{j}')
        return cols

    def get_state(self):
        if not self.is_in_play:
            return
        team_mate_positions = []
        return [
            *self.player_with_ball.position,
            *self.get_all_team_positions(),
            *[self.player_with_ball.get_fgp(bucket) for bucket in (assets.DistanceBucket.RESTRICTED_AREA, assets.DistanceBucket.IN_THE_PAINT, assets.DistanceBucket.MIDRANGE, assets.DistanceBucket.THREE_POINT_RANGE)],
            *[self.player_with_ball.get_stat(i) for i in self.get_pass_cols()],
            self.player_with_ball.get_stat('ftp'),
            self.player_with_ball.get_oreb(),
            self._find_player(self.defend_players, self.player_with_ball.data['position'].iloc[0]).get_steal(),
            self._find_player(self.defend_players, self.player_with_ball.data['position'].iloc[0]).get_block(),
            self._find_player(self.defend_players, self.player_with_ball.data['position'].iloc[0]).get_foul_percentage(),
            self._find_player(self.defend_players, self.player_with_ball.data['position'].iloc[0]).get_dreb(),
            self.distance_to_net(self.player_with_ball),
            int(self.is_at_three(self.player_with_ball)),
            self.time
        ]

    def _find_player(self, players_list, position):
        for i in players_list:
            if i.data['position'].iloc[0] == position:
                return i

    def _find_player_closeset_to(self, players_list, position):
        distances = []
        for i in players_list:
            point = Point(i.position[0], i.position[1])
            distances.append(position.distance(point))
        return players_list[np.argmax(distances)]

    def random_point_in_shp(self, shp):
        within = False
        while not within:
            x = np.random.uniform(shp.bounds[0], shp.bounds[2])
            y = np.random.uniform(shp.bounds[1], shp.bounds[3])
            within = shp.contains(Point(x, y))
        return (x, y)

    def initialize_players(self, csv_name, players_list, PlayerClass, read_func=pd.read_csv, random_position=True):
        if players_list:
            return
        df = read_func(self.path + csv_name).dropna(how='any')
        for i in df['name']:
            players_list.append(
                PlayerClass(
                    df,
                    i,
                    self.random_point_in_shp(self.player_region[df[df['name'] == i]['position'].iloc[0]].iloc[0].geometry),
                    name_column='name'
                )
            )
#        for i in players_list:
#            i.position = self.PLAYER_STARTING_POSITIONS[i.data['position'].iloc[0]]

    def initialize_offensive_players(self):
        self.initialize_players('AttackPlayer.csv', self.attack_players, AttackPlayer)

    def initialize_defensive_players(self):
        self.initialize_players('DefendPlayer.csv', self.defend_players, DefendPlayer)

    def initialize_managers(self):
        managers = [ShotManager, DribbleManager, PassManager, ReboundManager]
        manager_list = [self.shooting_managers, self.dribble_managers, self.passing_managers, self.rebound_managers]
        for manager in range(len(managers)):
            if manager_list[manager]:
                continue
            for i in self.attack_players:
                defender = self._find_player(self.defend_players, i.data['position'].iloc[0])
                manager_list[manager][i] = managers[manager](i, defender, [], self.court)

    def _shoot(self, player):
        manager = self.shooting_managers[player]
        reward = manager.field_goal()
        if reward < 0:
            closest_to_paint =  self._find_player_closeset_to(
                        self.attack_players,
                        self.court[self.court['name'] == 'in_the_paint'].geometry
                    )

            manager = self.rebound_managers[closest_to_paint]
            rebound_reward = manager.rebound()
            if rebound_reward > 0:
                self.player_with_ball = closest_to_paint
            else:
                self.is_in_play = False
            reward += rebound_reward
        else:
            self.is_in_play = False
        return reward

    def _pass(self, action):
        position_to = action.__str__().split('_')[-1]
        if self.player_with_ball.data['position'].iloc[0] == position_to:
            print('You can\'t pass to yourself, ya silly goose!')
            self.is_in_play = False
            return -10
        player_to = self._find_player(self.attack_players, position_to)
        manager = self.passing_managers[self.player_with_ball]
        reward = manager.pass_to(player_to)
        if reward >= 0:
            self.player_with_ball = player_to
        else:
            self.is_in_play = False
        return reward

    def _dribble(self, action):
        direction = action.__str__().split('_')[-1]
        manager = self.dribble_managers[self.player_with_ball]
        time_to_dribble, reward, fouled = manager.dribble(direction)
        self.time -= time_to_dribble
        if reward < 0 or fouled:
            self.is_in_play = False
        return reward

    def step(self, action):
        if self.time == 0:
            print(f"shot clock violation!")
            self.is_in_play = False
            return -10
        position = court.point_to_region(self.player_with_ball.position, self.court)
        print(f"{self.player_with_ball.data['name'].iloc[0]} has ball in {position}!")
        if action is assets.Action.SHOOT:
            self.time -= 1
            return self._shoot(self.player_with_ball)
        if action.value >= 5:
            self.time -= 1
            return self._pass(action)
        if 1 <= action.value <= 4:
            return self._dribble(action)

if __name__ == "__main__":
    env = BasketballEnvironment('./assets/datasets/')
    env.start()
    defe = env._find_player(env.defend_players, env.attack_players[0].data['position'][0])
    ap = env.attack_players[0]
    point_to_region = court.point_to_region(ap.position, env.court)
    reward = env._shoot(env.attack_players[0])
#    reward = env._pass(assets.Action.PASS_TO_SF)
    reward = env._dribble(assets.Action.DRIBBLE_FORWARD)
    print(env.get_state())
    print(len(env.get_state()))
