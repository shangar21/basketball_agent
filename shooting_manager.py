from assets import manager

class ShotManager(manager.Manager):
    def field_goal(self, shot_clock_bucket):
        shot_probability = self.adjust_stat(
            self.attack_player.get_fgp(self.attack_player.position),
            'shotclock',
            shot_clock_bucket
        )
        block_probability = self.defend_player.get_block()
        shot_attempt = self.attempt(shot_probability)
        block_attempt = self.attempt(block_probability)
        return shot_attempt, block_attempt

    def free_throw(self):
        return self.attempt(self.attack_player.get_stat('ftp'))
