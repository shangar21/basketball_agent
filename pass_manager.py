from assets import manager
from assets import court, assets

class PassManager(manager.Manager):
    def pass_to(self, player):
        box_1 = court.point_to_pass_region(self.attack_player.position, self.court)
        box_2 = court.point_to_pass_region(player.position, self.court)
        try:
            pass_probability = self.attack_player.get_stat(f'pass_box_{box_1}_{box_2}')
        except:
            pass_probability = 1
        steal_probability = self.defend_player.get_steal()
        pass_attempt = self.attempt(pass_probability)
        intercept_attempt = self.attempt(steal_probability)
        reward = self.pass_message(pass_attempt, intercept_attempt, player, box_2)
        return reward

    def pass_message(self, pass_attempt, intercept_attempt, player, p_box):
        print(f"{self.attack_player.data['name'].iloc[0]} passes to {player.data['name'].iloc[0]} in box {p_box}")
        if intercept_attempt is assets.Attempt.SUCCESS:
            print(f"{self.defend_player.data['name'].iloc[0]} intercepts pass!")
            return -1.5
        elif pass_attempt is assets.Attempt.SUCCESS:
            print(f"{self.attack_player.data['name'].iloc[0]} makes pass!")
            return 0
        else:
            print(f"{self.attack_player.data['name'].iloc[0]} missed pass!")
            return -1.5


