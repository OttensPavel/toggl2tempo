from enum import Enum


class WorkLogState(Enum):
    Unknown = -1
    Incomplete = 0
    New = 1
    Updated = 2
    Moved = 3
    Synced = 127
