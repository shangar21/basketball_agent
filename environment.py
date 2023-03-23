from attack_player import AttackPlayer
from defend_player import DefendPlayer
from shooting_manager import ShotManager
from pass_manager import PassManager
from assets import court, assets
import pandas as pd
import numpy as np
import shapely
import geopandas as gpd
from shapely.geometry import Point

class BasketballEnvironment():

    def __init__(self, dataset_path):
        self.path = dataset_path
        self.court, self.whole_court = court.initialize_court('./assets/court.geojson')
        self.attack_players = []
        self.defend_players = []
        self.shooting_managers = {}
        self.passing_managers = {}

    def start(self):
        self.initialize_offensive_players()
        self.initialize_defensive_players()
        self.initialize_shooting_manager()
        self.initialize_passing_manager()
        self.player_with_ball = self._find_player(self.attack_players, 'PG')

    def _find_player(self, players_list, position):
        for i in players_list:
            if i.data['position'].iloc[0] == position:
                return i

    def random_point_in_shp(self, shp):
        within = False
        while not within:
            x = np.random.uniform(shp.bounds[0], shp.bounds[2])
            y = np.random.uniform(shp.bounds[1], shp.bounds[3])
            within = shp.contains(Point(x, y))
        return (x, y)

    def initialize_players(self, csv_name, players_list, PlayerClass, read_func=pd.read_csv, random_position=True):
        df = read_func(self.path + csv_name)
        for i in df['name']:
            players_list.append(
                PlayerClass(
                    df,
                    i,
                    self.random_point_in_shp(self.whole_court),
                    name_column='name'
                )
            )

    def initialize_offensive_players(self):
        self.initialize_players('AttackPlayer.csv', self.attack_players, AttackPlayer)

    def initialize_defensive_players(self):
        self.initialize_players('DefendPlayer.csv', self.defend_players, DefendPlayer)

    def initialize_shooting_manager(self):
        for i in self.attack_players:
           defender = self._find_player(self.defend_players, i.data['position'].iloc[0])
           self.shooting_managers[i] = ShotManager(i, defender, [], self.court)

    def initialize_passing_manager(self):
        for i in self.attack_players:
           defender = self._find_player(self.defend_players, i.data['position'].iloc[0])
           self.passing_managers[i] = PassManager(i, defender, [], self.court)

    def _shoot(self, player):
       manager = self.shooting_managers[player]
       return manager.field_goal()

    def _pass(self, action):
        position_to = action.__str__().split('_')[-1]
        if self.player_with_ball.data['position'].iloc[0] == position_to:
            print('You can\'t pass to yourself, ya silly goose!')
            return -100000000
        player_to = self._find_player(self.attack_players, position_to)
        manager = self.passing_managers[self.player_with_ball]
        reward = manager.pass_to(player_to)
        if reward >= 0:
            self.player_with_ball = player_to
        return reward

    def step(self, action):
        print(f"{self.player_with_ball.data['name'].iloc[0]} has ball!")
        if action is assets.Action.SHOOT:
            return self._shoot(self.player_with_ball)
        if action.value >= 5:
            return self._pass(action)

if __name__ == "__main__":
    env = BasketballEnvironment('./assets/datasets/')
    env.start()
    defe = env._find_player(env.defend_players, env.attack_players[0].data['position'][0])
    ap = env.attack_players[0]
    point_to_region = court.point_to_region(ap.position, env.court)
    reward = env._shoot(env.attack_players[0])
    print(reward)
    reward = env._pass(assets.Action.PASS_TO_SF)

