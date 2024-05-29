import datetime 
import os 
import sys 
import logging

try:
    import RPi.GPIO as GPIO
except:
    print(f"couldnt import RPi, if not on a laptop something is wrong")


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))

from api.Relays.RelayController import RelayController
from api.Utility import Utility
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface
from api.Config import DeviceStatus
from Config import RELAY_PIN

logger = logging.getLogger(__name__)

class RelayControllerTarget(RelayController):
    """
    Actual relay controller class that will interact with the hardware
    relay device to turn on/off the connected device.
    """

    def __init__(self, db_interface: DbInterface):
        self.pin = RELAY_PIN
        self.__setup() 

        self.current_state: bool = False
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

    def __setup(self): 
        try:
            GPIO.setwarnings(False)  # Ignore warning for now
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)  
            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::setup {e}")
            return False

    def turn_on(self, effective_temperature: float = 0.0, reason="user action"):
        try:
            GPIO.output(self.pin, GPIO.HIGH) 

            ## update records  
            self.current_state = True
            columns: tuple = (
                SharedDataColumns.DEVICE_STATUS.value,
                SharedDataColumns.LAST_TURNED_ON.value,
            )
            new_values: tuple = (DeviceStatus.ON.value, self.utility.get_est_time_now())
            self.db_interface.update_multiple_columns(columns, new_values)
            state_info: tuple = (self.current_state, effective_temperature, reason)
            self.utility.record_state_transition(state_info)

            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::turn_on {e}")
            return False

    def turn_off(self, effective_temperature: float = 0.0, reason="user action"):
        try:
            GPIO.output(self.pin, GPIO.LOW) 

            ## update records 
            self.current_state = False 
            columns: tuple = (
                SharedDataColumns.DEVICE_STATUS.value,
                SharedDataColumns.LAST_TURNED_OFF.value,
            )
            new_values: tuple = (DeviceStatus.OFF.value, self.utility.get_est_time_now())
            self.db_interface.update_multiple_columns(columns, new_values)
            state_info: tuple = (self.current_state, effective_temperature, reason)
            self.utility.record_state_transition(state_info)

            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::turn_off {e}")
            return False
