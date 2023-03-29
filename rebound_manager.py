from assets import manager
from assets import assets

class ReboundManager(manager.Manager):
    def rebound(self):
        off_rebound = self.attempt(self.attack_player.get_oreb())
        def_rebound = self.attempt(self.defend_player.get_dreb())
        return self.rebound_message(off_rebound, def_rebound)

    def rebound_message(self, off_rebound, def_rebound):
        print(f'{self.attack_player.data["name"].iloc[0]} goes for rebound against {self.defend_player.data["name"].iloc[0]}!')
        if def_rebound is assets.Attempt.SUCCESS:
            print(f'{self.defend_player.data["name"].iloc[0]} get rebound!')
            return 0
        elif off_rebound is assets.Attempt.SUCCESS:
            print(f'{self.attack_player.data["name"].iloc[0]} get rebound!')
            return 0.5
        print('No rebounds won!')
        return 0

