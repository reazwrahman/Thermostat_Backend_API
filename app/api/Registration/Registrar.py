import os
import sys
import logging
from threading import Thread
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.Relays.RelayController import RelayController
from api.Sensors.TemperatureSensor import TemperatureSensor

logger = logging.getLogger(__name__)


class RunningModes(Enum):
    SIM = "simulation"
    TARGET = "target"


class Registrar:
    """
    Responsible for registering threads and controller objects
    """

    __registered_threads: set = (
        set()
    )  # set guarantees that each thread can only be registered once
    __registered_sensors: dict = dict()
    __registered_relays: dict = dict()

    @staticmethod
    def register_thread(new_thread: Thread):
        """
        register a new thread
        """
        Registrar.__registered_threads.add(new_thread)

    @staticmethod
    def get_registered_threads():
        """
        get the set of all registered threads
        """
        return Registrar.__registered_threads

    @staticmethod
    def register_temperature_sensor(
        temperature_sensor: TemperatureSensor, running_mode: RunningModes
    ):
        """
        register a new temeprature sensor instance
        """
        Registrar.__registered_sensors[running_mode] = temperature_sensor
        

    @staticmethod
    def get_temperature_sensor(running_mode: RunningModes):
        """
        get a registered temperature sensor
        """ 
        if running_mode in Registrar.__registered_sensors:
            return Registrar.__registered_sensors[running_mode]
        else:
            raise KeyError(
                f"Registrar::get_temperature_sensor {running_mode} is not registered"
            )

    @staticmethod
    def register_relay_controllers(
        relay_controller: RelayController, running_mode: RunningModes
    ):
        """
        register a new relay controller instance
        """
        Registrar.__registered_relays[running_mode] = relay_controller

    @staticmethod
    def get_relay_controllers(running_mode: RunningModes):
        """
        get a registered relay controller
        """
        if running_mode in Registrar.__registered_relays:
            return Registrar.__registered_relays[running_mode]
        else:
            raise KeyError(
                f"Registrar::get_relay_controllers {running_mode} is not registered"
            )
