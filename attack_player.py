import pandas as pd
from assets import player, assets

class AttackPlayer(player.Player):
    def get_fgp(self, distance_bucket):
        return self.get_stat('fgp_' + assets.distance_bucket_to_string(distance_bucket))

    def get_oreb(self):
        return self.get_stat('oreb')

    def get_passing_frequency(self, distance_bucket, box_number=''):
        stat_name = 'pass_freq_' + assets.distance_bucket_to_string(distance_bucket)
        if box_number:
            stat_name += str(box_number)
        return self.get_stat(stat_name)

