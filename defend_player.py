from assets import player
from pandas import pd

class DefendPlayer(player.Player):
    def get_steal(self):
        return self.get_stat('stlp')

    def get_block(self):
        return self.get_stat('blkp')

    def get_dreb(self):
        return self.get_stat('dreb')

    def get_foul_percentage(self):
        return self.get_stat('foulp')

