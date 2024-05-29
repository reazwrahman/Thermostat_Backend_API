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

from Relays.RelayController import RelayController
from Config import RELAY_PIN

logger = logging.getLogger(__name__)

class RelayControllerTarget(RelayController):
    """
    Actual relay controller class that will interact with the hardware
    relay device to turn on/off the connected device.
    """

    def __init__(self):
        self.pin = RELAY_PIN
        self.__setup()

    def __setup(self):
        try:
            GPIO.output(self.pin, GPIO.HIGH)
            return True
        except Exception as e:
            logger.error(f"RelayControllerTarget::setup {e}")
            return False

    def turn_on(self):
        try:
            GPIO.output(self.pin, GPIO.HIGH)
            return True
        except Exception as e:
            print(e)
            return False

    def turn_off(self):
        try:
            GPIO.output(self.pin, GPIO.LOW)
            return True
        except Exception as e:
            print(e)
            return False
