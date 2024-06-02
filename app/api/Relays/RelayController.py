import os
import sys
import logging
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.Utility import Utility
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface
from api.Config import DeviceStatus 

logger = logging.getLogger(__name__)


class RelayController:
    """
    base class
    """

    def __init__(self, db_interface: DbInterface):
        self.current_state: bool = False
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

    def setup(self):
        pass 

    def turn_on(self, effective_temperature: float = 0.0, reason="user action"):  
        if reason == "": 
            reason = "user action" 
        self.current_state = True
        try:
            columns: tuple = (
                SharedDataColumns.DEVICE_STATUS.value,
                SharedDataColumns.LAST_TURNED_ON.value,
            )
            new_values: tuple = (DeviceStatus.ON.value, datetime.datetime.now())
            self.db_interface.update_multiple_columns(columns, new_values)
            state_info: tuple = (self.current_state, effective_temperature, reason)
            self.utility.record_state_transition(state_info)
            return True
        except Exception as e:
            logger.error(
                f"RelayController::turn_on failed to set device status to True, exception:{str(e)}")
            
            return False

    def turn_off(self, effective_temperature: float = 0.0, reason="user action"): 
        if reason == "": 
            reason = "user action" 
            
        self.current_state = False
        try:
            columns: tuple = (
                SharedDataColumns.DEVICE_STATUS.value,
                SharedDataColumns.LAST_TURNED_OFF.value,
            )
            new_values: tuple = (DeviceStatus.OFF.value, datetime.datetime.now())
            self.db_interface.update_multiple_columns(columns, new_values)
            state_info: tuple = (self.current_state, effective_temperature, reason)
            self.utility.record_state_transition(state_info)
            return True
        except Exception as e:
            logger.error(
                f"RelayController::turn_off failed to set device status to False, exception:{str(e)}"
            )
            return False
