from attack_player import AttackPlayer
from defend_player import DefendPlayer
from shooting_manager import ShotManager
from assets import court, assets
import pandas as pd
import numpy as np
import shapely
import geopandas as gpd

class BasketballEnvironment():

    def __init__(self, dataset_path):
        self.path = dataset_path
        self.court, self.whole_court = court.initialize_court('./assets/court.geojson')
        self.attack_players = []
        self.defend_players = []
        self.shooting_managers = {}

    def start(self):
        self.initialize_offensive_players()
        self.initialize_defensive_players()
        self.initialize_shooting_manager()
        self.player_with_ball = self._find_player(self.attack_players, 'PG')

    def _find_player(self, players_list, position):
        for i in players_list:
            if i.data['position'].iloc[0] == position:
                return i

    def initialize_players(self, csv_name, players_list, PlayerClass, read_func=pd.read_csv, random_position=True):
        df = read_func(self.path + csv_name)
        minx, miny, maxx, maxy = self.whole_court.bounds
        for i in df['name']:
            players_list.append(
                PlayerClass(
                    df,
                    i,
                    (np.random.randint(minx, maxx), np.random.randint(miny, maxy)),
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

    def _shoot(self, player):
       manager = self.shooting_managers[player]
       return manager.field_goal()

    def step(self, action):
        if action is assets.Action.SHOOT:
            return self._shoot(self.player_with_ball)



if __name__ == "__main__":
    env = BasketballEnvironment('./assets/datasets/')
    env.start()
    defe = env._find_player(env.defend_players, env.attack_players[0].data['position'][0])
    ap = env.attack_players[0]
    point_to_region = court.point_to_region(ap.position, env.court)
    reward = env._shoot(env.attack_players[0])
    print(reward)

