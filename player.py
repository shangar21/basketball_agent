from enum import Enum
import numpy as np
from functools import total_ordering

'''
field goal percentage dict:
{
    '<5': 0.1, # less than 5 feet
    '5-9': 0.2, # 5 - 9 feet
    '10-14': 0.3,
    '15-19': 0.4,
    '20-24': 0.5,
    '25-29':0.6
}
'''

class Attempt(Enum):
    SUCCESS = 1
    FAIL = 0
    FOUL = -1

class DistanceBucket(Enum):
    RESTRICTED_AREA = 0
    IN_THE_PAINT = 1
    MIDRANGE = 2
    LEFT_CORNER_THREE = 3
    RIGHT_CORNER_THREE = 3
    ABOVE_THE_BREAK_THREE = 4

class Player():
    def __init__(self, name, fgp, ftp, orebp, drebp, astp, tovp, stlp, blkp, pfp, distance):
        self.name = name
        self.fgp = fgp
        self.ftp = ftp
        self.orebp = orebp
        self.drebp = drebp
        self.astp = astp
        self.tovp = tovp
        self.stlp = stlp
        self.blkp = blkp
        self.pfp = pfp
        self.distance = distance

    def _attempt(self, stat):
        if np.random.uniform() < stat:
            return Attempt.SUCCESS
        return Attempt.FAIL

    def field_goal(self):
        return self._attempt(self.fgp[self.distance])

    def free_throw(self):
        return self._attempt(self.ftp)

    def assist(self):
        return self._attempt(self.astp)

    def offensive_rebound(self):
        return self._attempt(self.orebp)

    def defensive_rebound(self):
        return self._attempt(self.drebp)

    def _attempt_defence(self, stat):
        if self._attempt(self.pfp) is Attempt.SUCCESS:
            return Attempt.FOUL
        return self._attempt(stat)

    def steal(self):
        return self._attempt_defence(self.stlp)

    def block(self):
        return self._attempt_defence(self.blkp)
