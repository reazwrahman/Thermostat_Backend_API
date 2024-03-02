import os
import sys
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from app.api.Registration.Registrar import RunningModes

RUNNING_MODE = RunningModes.SIM  ## the mode we are running the application in

MINIMUM_ON_TIME = 3  # minutes
COOL_DOWN_PERIOD = 3  # minutes
MAXIMUM_ON_TIME = 15  # minutes


class DeviceStatus(Enum):
    ON = "ON"
    OFF = "OFF"
