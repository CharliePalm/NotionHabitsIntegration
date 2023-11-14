from enum import Enum

class Frequency(Enum):
    Daily = '0'
    Weekly = '1'
    Monthly = '2'
    Cyclic = '3'
    
DEFAULT_CYCLE_ICON = '🌘'