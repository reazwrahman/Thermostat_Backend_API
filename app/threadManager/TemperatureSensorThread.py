from threading import Thread
import time
import logging
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
api_dir = os.path.join(parent_dir, "api")
sys.path.append(api_dir)

from api.DatabaseAccess.DbTables import SharedDataColumns
from api.Config import DeviceStatus
from app.api.Registration.Registrar import Registrar
from api.Config import RUNNING_MODE
from api.Sensors.TemperatureSensor import TemperatureSensor

DELAY_BETWEEN_READS = 1  # take a read every n seconds
SAMPLE_SIZE = 5  # take average of n reads before taking any action

logger = logging.getLogger(__name__)


class TemperatureSensorThread(Thread):
    """
    CPU thread responsible for reading temeprature sensor
    value in a regular cadence
    """

    def __init__(self, thread_name="TemperatureSensorThread", **kwargs):
        Thread.__init__(self)
        self.registrar = Registrar()
        print(f"TemperatureSensorThread registrar id = {id(self.registrar)}")
        print(f"im temp thread im calling registrar with {RUNNING_MODE.value}")
        self.thermo_stat: TemperatureSensor = self.registrar.get_temperature_sensor(
            RUNNING_MODE.value
        )
        self.thread_name = thread_name
        self.keep_me_alive = True
        self.db_interface = kwargs["db_interface"]
        self.temperature_history: list = []

    def run(self):
        """
        main thread that runs continuously. Update every n seconds,
        with the running average of n sample data
        """
        while self.keep_me_alive:
            device_status = self.db_interface.read_column(
                SharedDataColumns.DEVICE_STATUS.value
            )
            current_temp: float = self.thermo_stat.get_temperature(
                device_status == DeviceStatus.ON.value
            )
            self.temperature_history.append(current_temp)
            if len(self.temperature_history) >= SAMPLE_SIZE:
                running_avg = round(sum(self.temperature_history) / SAMPLE_SIZE)

                self.db_interface.update_column(
                    SharedDataColumns.LAST_TEMPERATURE.value, running_avg
                )
                self.temperature_history = []  # reset batch
            logging.info(f"Current Temperature: {current_temp}")
            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        self.keep_me_alive = False
        logging.info(f"{self.thread_name} is terminated")
