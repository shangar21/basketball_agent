import pandas as pd
from assets import player, assets

class AttackPlayer(player.Player):
    shot_pad = {
        assets.DistanceBucket.RESTRICTED_AREA: 0.28,
        assets.DistanceBucket.IN_THE_PAINT: 0.5,
        assets.DistanceBucket.MIDRANGE: 0.3,
        assets.DistanceBucket.THREE_POINT_RANGE: 0,
    }
    def get_fgp(self, distance_bucket):
        return self.get_stat('fgp_' + assets.distance_bucket_to_string(distance_bucket).lower()) + self.shot_pad[distance_bucket]

    def get_tpp(self):
        return self.get_stat('tpp')

    def get_oreb(self):
        return self.get_stat('oreb')


