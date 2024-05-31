import os
import sys
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)


class DeviceTypes(Enum):
    HEATER = "HEATER"
    AC = "AC"

class DeviceStatus(Enum):
    ON = "ON"
    OFF = "OFF"


class RunningModes(Enum):
    SIM = "simulation"
    TARGET = "target"


RUNNING_MODE = RunningModes.SIM  ## the mode we are running the application in

MINIMUM_ON_TIME = 1  # minutes
COOL_DOWN_PERIOD = 1  # minutes
MAXIMUM_ON_TIME = 2  # minutes 

SENSOR_PIN = 4 # GPIO PIN on raspberry pi 
RELAY_PIN = 6 # GPIO PIN on raspberry pi  

SWITCH_KEY = "90e96885-cb29-432d-8450-e018ab042114"
