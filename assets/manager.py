import numpy as np
from .assets import Attempt

class Manager():
    def __init__(self, attack_player, defend_player, coefficients, court):
        self.attack_player = attack_player
        self.defend_player = defend_player
        self.coefficients = coefficients
        self.court = court

    def get_coefficient(self, coefficient):
        if coefficient in self.coefficients:
            return self.coefficients[coefficient]
        return 0

    def adjust_stat(self, stat, coefficient, state, offensive=True):
        player = self.attack_player if offensive else self.defend_player
        return player.get_stat(stat) + get_coefficient(coefficient) * state

    def attempt(self, probability):
        p = np.random.uniform(0, 1)
        if p <= probability:
            return  Attempt.SUCCESS
        else:
            return Attempt.FAIL

    def attempt_defense(self, probability, foul_probability):
        foul = self.attempt(foul_probability)
        if foul is Attempt.SUCCESS:
            return Attempt.FOUL
        else:
            return self.attempt(probability)
