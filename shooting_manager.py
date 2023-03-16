from assets import manager
from assets import court, assets

class ShotManager(manager.Manager):
    def field_goal(self):
        distance_bucket = court.point_to_region(self.attack_player.position, self.court)
        shot_probability = self.attack_player.get_fgp(distance_bucket)
        block_probability = self.defend_player.get_block()
        foul_probability = self.defend_player.get_stat('foulp')
        shot_attempt = self.attempt(shot_probability)
        block_attempt = self.attempt_defense(block_probability, foul_probability)
        return self.fg_message(shot_attempt, block_attempt, distance_bucket)

    def fg_message(self, shot, block, distance_bucket):
        print(f"{self.attack_player.data['name'].iloc[0]} takes shot from {distance_bucket}.")
        if block is assets.Attempt.SUCCESS:
            print(f"{self.defend_player.data['name'].iloc[0]} blocks shot.")
            return -1.5
        elif block is assets.Attempt.FOUL:
            print(f"{self.defend_player.data['name'].iloc[0]} fouls!")
            return self.foul_manager(shot, distance_bucket)
        elif shot is assets.Attempt.SUCCESS:
            print(f"{self.attack_player.data['name'].iloc[0]} makes shot!")
            if distance_bucket.value >= 3:
                return 3
            return 2
        else:
            print(f"{self.attack_player.data['name'].iloc[0]} missed shot!")
            return -1.5

    def free_throw(self, nft):
        reward = 0
        for i in range(nft):
            ft = self.attempt(self.attack_player.get_stat('ftp'))
            if ft is assets.Attempt.SUCCESS:
                print(f"Free throw made!")
                reward += 1
            else:
                print(f"Free throw missed!")
        return reward

    def foul_manager(self, shot, distance_bucket):
        reward = 0
        nft = 2
        if shot is assets.Attempt.SUCCESS:
            reward += 3 if distance_bucket.value >= 3 else 2
            print(f"{self.attack_player.data['name'].iloc[0]} makes shot! And 1 Awarded")
            nft = 1
        print(f"{self.attack_player.data['name'].iloc[0]} attempts free throws!")
        return self.free_throw(nft)

