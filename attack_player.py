import pandas as pd
from assets import player, assets

class AttackPlayer(player.Player):
    def get_fgp(self, distance_bucket):
        return self.get_stat('fgp_' + assets.distance_bucket_to_string(distance_bucket).lower())

    def get_tpp(self):
        return self.get_stat('tpp')

    def get_oreb(self):
        return self.get_stat('oreb')


