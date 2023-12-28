from enum import Enum, auto

class Move(Enum):
    SerialMove = auto()
    ParallelMove = auto()
    ConditionalMove = auto()