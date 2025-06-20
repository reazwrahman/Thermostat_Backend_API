import os
import sys
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.DatabaseAccess.DbTables import SharedDataColumns

db_api: DbInterface = DbInterface()


class DeviceTypes(Enum):
    HEATER = "HEATER"
    AC = "AC"
    FAN = "FAN"


class DeviceStatus(Enum):
    ON = "ON"
    OFF = "OFF"


class ThermoStatActions(Enum):
    ON = "ON"
    OFF = "OFF"
    UPDATE = "UPDATE"


class RunningModes(Enum):
    SIM = "simulation"
    TARGET = "target"


## ALL THE AVAILABLE CONCURRENT THREADS
THERMO_THREAD = "thermo_thread"
AC_THREAD = "ac_thread"
FAN_THREAD = "fan_thread"
TEMP_SENSOR_THREAD = "temperature_sensor_thread"

## Device to thread mapping
DEVICE_TO_THREAD_MAP = {
    DeviceTypes.AC.value: AC_THREAD,
    DeviceTypes.HEATER.value: THERMO_THREAD,
    DeviceTypes.FAN.value: FAN_THREAD
}

RUNNING_MODE = RunningModes.TARGET  ## the mode we are running the application in

SENSOR_PIN = 4  # GPIO PIN on raspberry pi
RELAY_PIN = 6  # GPIO PIN on raspberry pi

SWITCH_KEY = "90e96885-cb29-432d-8450-e018ab042114"

DEVICE_CONFIGS = { 
    "HEATER":{ 
        "minimum_on_time": 3, 
        "maximum_on_time": 1440, 
        "cooldown_period" : 3
    },  
    "FAN":{ 
        "minimum_on_time": 3, 
        "maximum_on_time": 1440, 
        "cooldown_period" : 1
    },
    "AC":{ 
        "minimum_on_time": 20, 
        "maximum_on_time": 120, 
        "cooldown_period" : 15
    },

}