from enum import Enum

class Attempt(Enum):
    SUCCESS = 1
    FAIL = 0
    FOUL = -1

class DistanceBucket(Enum):
    RESTRICTED_AREA = 0
    IN_THE_PAINT = 1
    MIDRANGE = 2
    MIDRANGE_BOX_1 = 2
    MIDRANGE_BOX_2 = 2
    MIDRANGE_BOX_3 = 2
    MIDRANGE_BOX_4 = 2
    MIDRANGE_BOX_5 = 2
    LEFT_CORNER_THREE = 3
    RIGHT_CORNER_THREE = 3
    ABOVE_THE_BREAK_THREE = 4
    ABOVE_THE_BREAK_THREE_1 = 4
    ABOVE_THE_BREAK_THREE_2 = 4
    ABOVE_THE_BREAK_THREE_3 = 4

class ShotclockBucket(Enum):
    TIME_24_22 = 1
    TIME_22_18 = 2
    TIME_18_15 = 3
    TIME_15_7 = 4
    TIME_7_4 = 5
    TIME_4_0 = 6

def distance_bucket_to_string(distance_bucket):
    return distance_bucket.__str__().replace('DistanceBucket.', '')
