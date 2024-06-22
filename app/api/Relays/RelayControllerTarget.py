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

        super().__init__(db_interface)

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
            super().turn_on(effective_temperature, reason)
            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::turn_on {e}")
            return False

    def turn_off(self, effective_temperature: float = 0.0, reason="user action"):
        try:
            GPIO.output(self.pin, GPIO.LOW)
            super().turn_off(effective_temperature, reason)
            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::turn_off {e}")
            return False
