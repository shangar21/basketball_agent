import numpy as np
from .assets import Attempt

class Manager():
    def __init__(self, attack_player, defend_player, coefficients):
        self.attack_player = attack_player
        self.defend_player = defend_player
        self.coefficients = coefficients

    def get_coefficient(self, coefficient):
        return self.coefficients[coefficient]

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
