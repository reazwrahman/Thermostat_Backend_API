from threading import Thread
import time
import logging
import datetime
import os

from api.Relays.PowerControlGateKeeper import PowerControlGateKeeper, States
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface
from api.Utility import Utility
from api.Config import MAXIMUM_ON_TIME

DELAY_BETWEEN_READS = 10  # take a read every n seconds

logger = logging.getLogger(__name__)


class ACThread(Thread):
    """
    CPU thread responsible triggering power relay for air conditioner depending on
    current temperature and target temperature
    """

    def __init__(self, thread_name="ThermoStatThread", **kwargs):
        Thread.__init__(self)
        self.thread_name = thread_name
        self.target_temp = kwargs["target_temperature"]  
        self.target_humidity = kwargs.get("target_humidity") ## optional argument
        self.db_interface: DbInterface = kwargs["db_interface"]
        self.keep_me_alive = True
        self.current_temperature: float = None
        self.current_humidity:float = None
        self.utility = Utility()

        self.__gate_keeper: PowerControlGateKeeper = PowerControlGateKeeper(
            db_interface=kwargs["db_interface"]
        )
        self.db_interface.update_column(
            SharedDataColumns.TARGET_TEMPERATURE.value, self.target_temp
        )

    def run(self):
        """
        main thread that runs continuously. Read current temperature
        at regular intervals, take running average and trigger relay.
        """
        while self.keep_me_alive:
            (
                self.current_temp,
                self.current_humidity,
                self.target_temp,
            ) = self.db_interface.read_multiple_columns(
                (
                    SharedDataColumns.LAST_TEMPERATURE.value, 
                    SharedDataColumns.LAST_HUMIDITY.value,
                    SharedDataColumns.TARGET_TEMPERATURE.value,
                )
            )
            status = self.__check_device_on_time()
            if status != States.TURNED_OFF:
                if self.current_temp:
                    if self.current_temp >= self.target_temp:
                        status = self.__gate_keeper.turn_on(
                            effective_temperature=self.current_temp,
                            reason="Current Temperature is above target temperature",
                        )  
                    else:
                        status = self.__gate_keeper.turn_off(
                            effective_temperature=self.current_temp,
                            reason="Current Temperature is below target temperature",
                        ) 

                    ## Humidity based actions are turned off for now 
                    '''elif self.current_humidity >= self.target_humidity:
                        status = self.__gate_keeper.turn_on(
                            effective_temperature=self.current_temp,
                            reason="Current humidity is above target humidity",
                        )'''
                    

            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        self.keep_me_alive = False
        logging.warn(f"{self.thread_name} is terminated")

    def __check_device_on_time(self):
        """
        checks if device on time has exceeded the max threshold
        """
        last_turned_on: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_ON.value
        )
        if last_turned_on:
            time_difference = self.utility.get_time_delta(last_turned_on)
            if time_difference >= MAXIMUM_ON_TIME:
                logger.warn(
                    "ACThread::__check_heater_on_time Device's maximum on time has exceeded"
                )
                status = self.__gate_keeper.turn_off(
                    effective_temperature=self.current_temp,
                    reason="Device's maximum on time has exceeded",
                )
                return status

        return States.NO_ACTION
