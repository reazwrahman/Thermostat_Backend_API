import datetime 
import pytz
import json
import logging
from enum import Enum
import os
import sys 
import datetime


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface 
from api.DatabaseAccess.DbTables import SharedDataColumns 
from UtilLogHelper import UtilLogHelper

logger = logging.getLogger(__name__)


STATE_CHANGE_LOGGER = "state_transition_record.txt"
MAX_RECORDS_TO_STORE = 20


class Utility:
    """
    This class provides general utility services required by other components
    in this program.
    """

    state_transition_counter = 0  # static attribute to track total events recorded 

    def __init__(self, state_record_file=None, max_capacity=None):
        self.__db_interface = DbInterface()

        if not state_record_file:
            self.state_record_storage = STATE_CHANGE_LOGGER
        else:
            self.state_record_storage = state_record_file

        if not max_capacity:
            self.max_record_capacity = MAX_RECORDS_TO_STORE
        else:
            self.max_record_capacity = max_capacity

    def __repr__(self):
        """
        returns the core purpose of this class
        """
        return "Provides general utility services to other components in this smart thermostat program."

    def __len__(self):
        """
        return the amount of records stored in the state transition record
        by all instances combined
        """
        return Utility.state_transition_counter

    def record_state_transition(self, state_data: tuple):
        """
        Record state transition events by providing specific information
        """
        status: bool = state_data[0]
        effective_temperature: float = state_data[1]
        reason: str = state_data[2]

        ## read required values from database
        query_result: tuple = self.__db_interface.read_multiple_columns(
            (
                SharedDataColumns.TARGET_TEMPERATURE.value,
                SharedDataColumns.LAST_TURNED_ON.value,
                SharedDataColumns.LAST_TURNED_OFF.value,
            )
        )
        payload = dict()

        ## populate payload from input state information
        if status:
            payload["state_change"] = "Device Turned On"
        else:
            payload["state_change"] = "Device Turned Off"
        payload["state_change_cause"] = reason
        payload["effective_temperature"] = effective_temperature

        ## populate payload from database
        payload["target_temperature"] = query_result[0]
        payload["last_turned_on"] = query_result[1]
        payload["last_turned_off"] = query_result[2]

        ## populate payload with time deltas
        payload["current_timestamp"] = str(datetime.datetime.now())
        payload["on_for_minutes"] = self.get_time_delta(payload["last_turned_on"])
        payload["off_for_minutes"] = self.get_time_delta(payload["last_turned_off"])

        self.write_to_file(payload)
        self.__log_payload(payload)  
        UtilLogHelper.record_state_changes_in_deque(payload)

    def get_time_delta(self, past_timestamp: str):
        """
        takes a timestamp in the past, calculates the delta from current time
        in minutes and returns the delta
        """
        time_now = datetime.datetime.now()
        delta = ""
        if past_timestamp:
            past_timestamp = datetime.datetime.strptime(
                past_timestamp, "%Y-%m-%d %H:%M:%S.%f"
            )
            delta = round((time_now - past_timestamp).total_seconds() / 60, 2)

        return delta

    def record_state_transition_with_payload(self, payload):
        """
        Record state transition events by providing the full payload
        """
        self.write_to_file(payload)
        self.__log_payload(payload) 
    
    def write_to_file(self, payload: dict):
        """
        private method to write payload to a text file
        """
        write_mode = None
        if os.path.exists(os.path.join(os.getcwd(), self.state_record_storage)):
            write_mode = "a"
        else:
            write_mode = "w"

        with open(self.state_record_storage, write_mode) as file:
            for key, value in payload.items():
                file.write(f"{key}: {value} \n")
            file.write("\n")

        Utility.state_transition_counter += 1
        self.__delete_older_records()

    def __log_payload(self, payload: dict):
        """
        logs the given payload to terminal
        """
        if len(payload) > 0:
            # log the state transition
            logging.info("====================================")
            logger.info("Dictionary: %s", payload)
            logging.info("====================================")
            return True
        else:
            logger.error("Utility::__log_payload No payload is provided to log")
            return False

    def __delete_older_records(self):
        """
        delete old record logging file and start fresh,
        if max storage limit reached
        """
        if Utility.state_transition_counter >= self.max_record_capacity:
            path = os.path.join(os.getcwd(), self.state_record_storage)
            os.remove(path)
            Utility.state_transition_counter = 0  # restart counter  
    
    def get_est_time_now(self): 
        est = pytz.timezone('US/Eastern')  
        current_est_time = datetime.datetime.now(est) 
        return current_est_time.strftime('%Y-%m-%d %H:%M')  
    
    def trim_to_minute(self, time_str): 
        if (time_str):
            date_part, time_part = time_str.split(' ')
            hour, minute, second_with_micro = time_part.split(':')
            second, microsecond = second_with_micro.split('.')
            trimmed_time_str = f"{date_part} {hour}:{minute}"

            return trimmed_time_str 
        else: 
            return time_str

    
    def get_latest_state(self):  
        timestamp = self.get_est_time_now()
        db_row:tuple = self.__db_interface.read_multiple_columns((SharedDataColumns.DEVICE_STATUS.value, 
                                                  SharedDataColumns.LAST_TEMPERATURE.value,  
                                                  SharedDataColumns.LAST_HUMIDITY.value, 
                                                  SharedDataColumns.LAST_TURNED_ON.value, 
                                                  SharedDataColumns.LAST_TURNED_OFF.value, 
                                                  SharedDataColumns.TARGET_TEMPERATURE.value))
        
        payload = {SharedDataColumns.DEVICE_STATUS.value: db_row[0],  
                   SharedDataColumns.LAST_TEMPERATURE.value: db_row[1],  
                   SharedDataColumns.LAST_HUMIDITY.value: db_row[2],
                   SharedDataColumns.LAST_TURNED_ON.value: self.trim_to_minute(db_row[3]), 
                   SharedDataColumns.LAST_TURNED_OFF.value: self.trim_to_minute(db_row[4]), 
                   SharedDataColumns.TARGET_TEMPERATURE.value: db_row[5], 
                   "timestamp": timestamp
        } 

        return payload
    

if __name__ == "__main__":
    utility = Utility(
        state_record_file=STATE_CHANGE_LOGGER, max_capacity=MAX_RECORDS_TO_STORE
    )
    ## test get time delta
    time_now = datetime.datetime.now()
    delta = 15
    past_time = str(time_now - datetime.timedelta(minutes=delta))
    assert (
        utility.get_time_delta(past_time) == delta
    ), "Utility::get_time_delta failed to calculate time difference" 
 
    ## test trim_to_minute()
    test_str = "2024-05-28 22:02:40.351332" 
    assert(utility.trim_to_minute(test_str) == "2024-05-28 22:02")

    ## test write_to_file
    test_payload = {"test_id": 100, "event": "off"}
    utility.write_to_file(test_payload)
    assert (
        os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)) == True
    ), "Utility::write_to_file failed to write to file"

    ## test the magic method __len__
    assert len(utility) == 1, "Utility::__len__ returns wrong counter"

    ## test delete older record capability
    if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)):
        os.remove(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER))
    Utility.state_transition_counter = 0

    test_payload = {"test_id": 1, "event": "on"}
    capacity_left = 2
    for i in range(MAX_RECORDS_TO_STORE - capacity_left):
        utility.record_state_transition_with_payload(test_payload)

    assert (
        os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)) == True
    ), "State transition record didn't get created or got deleted prematuredly"

    utility2 = Utility(
        state_record_file=STATE_CHANGE_LOGGER, max_capacity=MAX_RECORDS_TO_STORE
    )
    ## force deletion of the state record file
    for i in range(capacity_left):
        utility2.record_state_transition_with_payload(test_payload)

    assert (
        os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)) == False
    ), "State transition record didn't get deleted as expected"
    print("Utility class: all unit tests passed")
