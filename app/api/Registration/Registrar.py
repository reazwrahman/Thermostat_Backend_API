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
from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.Sensors.TemperatureSensorSim import TemperatureSensorSim
from app.api.Sensors.TemperatureSensorTarget import TemperatureSensorTarget
from app.api.Relays.RelayControllerSim import RelayControllerSim
from app.api.Relays.RelayControllerTarget import RelayControllerTarget 
from app.api.Config import RunningModes

logger = logging.getLogger(__name__)



class Registrar:
    """
    Responsible for registering controller objects
    """ 
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
 
    def __init__(self):
        self.__registered_sensors: dict = dict()
        self.__registered_relays: dict = dict() 
        self.db_api = DbInterface() 
        self.initialize()

    def initialize(self): 
        ## register all sensors
        simulation_sensor = TemperatureSensorSim()
        target_sensor = TemperatureSensorTarget()
        self.register_temperature_sensor(simulation_sensor, RunningModes.SIM.value)
        self.register_temperature_sensor(target_sensor, RunningModes.TARGET.value)

        ## register all relay controllers
        simulation_relay = RelayControllerSim(db_interface=self.db_api)
        target_relay = RelayControllerTarget()
        self.register_relay_controllers(simulation_relay, RunningModes.SIM.value)
        self.register_relay_controllers(target_relay, RunningModes.TARGET.value)

    def register_temperature_sensor(
        self, temperature_sensor: TemperatureSensor, running_mode: RunningModes
    ):
        """
        register a new temeprature sensor instance
        """
        self.__registered_sensors[running_mode] = temperature_sensor

    def get_temperature_sensor(self, running_mode: str):
        """
        get a registered temperature sensor
        """ 
        if running_mode in self.__registered_sensors:
            return self.__registered_sensors[running_mode]
        else:
            raise KeyError(
                f"Registrar::get_temperature_sensor {running_mode} is not registered"
            )

    def register_relay_controllers(
        self, relay_controller: RelayController, running_mode: RunningModes
    ):
        """
        register a new relay controller instance
        """
        self.__registered_relays[running_mode] = relay_controller 


    def get_relay_controllers(self, running_mode: str):
        """
        get a registered relay controller
        """ 
        if running_mode in self.__registered_relays:
            return self.__registered_relays[running_mode]
        else:
            raise KeyError(
                f"Registrar::get_relay_controllers {running_mode} is not registered"
            )
