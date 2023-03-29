from assets import manager, assets
from shooting_manager import ShotManager
import numpy as np
from shapely import Point

class DribbleManager(manager.Manager):
    dribble_info = {
        'PG': {'speed': 4.53, 'dribble_per_sec': 1.37, 'distance_per_dribble': 3.27},
        'SG': {'speed': 4.53, 'dribble_per_sec': 1.37, 'distance_per_dribble': 3.27},
        'SF': {'speed': 4.47, 'dribble_per_sec': 2.16, 'distance_per_dribble': 2.21},
        'PF': {'speed': 4.47, 'dribble_per_sec': 2.16, 'distance_per_dribble': 2.21},
        'C': {'speed': 4.36, 'dribble_per_sec': 3.18, 'distance_per_dribble': 1.42}
    }

    direction_to_vec = {
        'RIGHT': (1, 0),
        'FORWARD': (0, -1),
        'LEFT': (-1, 0),
        'BACKWARDS': (0, 1)
    }

    def calculate_time_and_num_dribbles(self, starting_pos, direction, player_position):
        player = self.dribble_info[player_position]
        distance = player['distance_per_dribble']
        time_to_move = distance / player['speed']
        num_dribbles = int(time_to_move * player['dribble_per_sec'])
        return round(time_to_move,2), num_dribbles

    def dribble(self, direction):
        steal = self.attempt_defense(self.defend_player.get_steal(), self.defend_player.get_foul_percentage())
        time_to_dribble, num_dribbles = self.calculate_time_and_num_dribbles(self.attack_player.position, direction, self.attack_player.data['position'].iloc[0])
        reward = self.dribble_message(direction, steal)
        return time_to_dribble, reward, steal is assets.Attempt.FOUL

    def get_new_pos(self, direction):
        current_pos = np.array(self.attack_player.position)
        new_pos = current_pos + self.direction_to_vec[direction]
        return tuple(new_pos)

    def check_valid_direction(self, direction):
        new_pos = self.get_new_pos(direction)
        point = Point(new_pos[0], new_pos[1])
        return len(self.court[self.court.geometry.contains(point)]) != 0

    def dribble_message(self, direction, steal):
        if not self.check_valid_direction(direction):
            print(f'{self.attack_player.data["name"].iloc[0]} dribbles out of bounds!')
            return -5
        print(f'{self.attack_player.data["name"].iloc[0]} dribbles {direction}!')
        if steal is assets.Attempt.SUCCESS:
            print(f'{self.defend_player.data["name"].iloc[0]} steals ball!')
            return -0.5
        elif steal is assets.Attempt.FOUL:
            print(f'{self.defend_player.data["name"].iloc[0]} fouls!')
            shooting_manager = ShotManager(self.attack_player, self.defend_player, [], self.court)
            return shooting_manager.foul_manager(assets.Attempt.FAIL, assets.DistanceBucket.MIDRANGE)
        else:
            self.attack_player.position = tuple(np.array(self.attack_player.position) + np.array(self.direction_to_vec[direction]))
            return 0



