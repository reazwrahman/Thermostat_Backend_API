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
SAMPLE_SIZE = 10  # take average of n reads before taking any action

logger = logging.getLogger(__name__)


class TemperatureSensorThread(Thread):
    """
    CPU thread responsible for reading temeprature sensor
    value in a regular cadence
    """

    def __init__(self, thread_name="TemperatureSensorThread", **kwargs):
        Thread.__init__(self)
        self.registrar = Registrar()
        self.thermo_stat: TemperatureSensor = self.registrar.get_temperature_sensor(
            RUNNING_MODE.value
        )
        self.thread_name = thread_name
        self.keep_me_alive = True
        self.db_interface = kwargs["db_interface"]
        self.temperature_history: list = [] 
        self.humidity_history: list = [] 

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
            current_humidity: float = self.thermo_stat.get_humidity()  

            self.update_sensor_reading(current_temp, self.temperature_history, SharedDataColumns.LAST_TEMPERATURE.value)  
            self.update_sensor_reading(current_humidity, self.humidity_history, SharedDataColumns.LAST_HUMIDITY.value) 
 

    def update_sensor_reading(self, sensor_reading, batch, db_column): 
        if (sensor_reading is not None): 
            batch.append(sensor_reading)  
        
        logging.info(f"{db_column}: {sensor_reading}") 
        logging.info(f" batch {db_column}: {batch}") 
        
        if len(batch) >= SAMPLE_SIZE:
            running_avg = self.__get_median_reading(batch)

            self.db_interface.update_column(
                db_column, running_avg
            ) 
            # reset batch  
            for i in range (len(batch)): 
                batch.pop() 
            
        time.sleep(DELAY_BETWEEN_READS)


    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        self.keep_me_alive = False
        logging.info(f"{self.thread_name} is terminated") 

    
    def __get_avg_reading(self, batch:list): 
        return round((sum(batch) / SAMPLE_SIZE),1) 
    
    def __get_median_reading(self, batch:list):  
        batch.sort()  
        mid_index:int = int(SAMPLE_SIZE/2)
        median:float = batch[mid_index] 
        return round(median,1) 

