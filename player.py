from enum import Enum
import numpy

class Attempt(Enum):
    SUCCESS = 1
    FAIL = 0
    FOUL = -1

class Player():
    def __init__(self, fgp, tpp, ftp, orebp, drebp, astp, tovp, stlp, blkp, pfp):
        self.fgp = fgp
        self.tpp = tpp
        self.ftp = ftp
        self.orebp = orebp
        self.drebp = drebp
        self.astp = astp
        self.tovp = tovp
        self.stlp = stlp
        self.blkp = blkp
        self.pfp = pfp

    def _attempt(self, stat):
        if np.random.uniform() < stat:
            return Attempt.SUCCESS
        return Attempt.FAIL

    def field_goal(self):
        return self._attempt(self.fgp)

    def three_point(self):
        return self._attempt(self.tpp)

    def free_throw(self):
        return self._attempt(self.ftp)

    def assist(self):
        return self._attempt(self.astp)

    def _attempt_defence(self, stat):
        if self._attempt(self.pfp):
            return Attempt.FOUL
        return self._attempt(stat)

    def steal(self):
        return self._attempt_defence(self.stlp)

    def block(self):
        return self._attempt_defence(self.blkp)
