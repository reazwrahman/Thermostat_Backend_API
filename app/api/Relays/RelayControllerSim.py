import os
import sys
import logging
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.Relays.RelayController import RelayController
from api.Utility import Utility
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface
from api.Config import DeviceStatus

logger = logging.getLogger(__name__)


class RelayControllerSim(RelayController):
    """
    Simulation class intended to mimic the behavior of the actual
    relay controller class.
    """

    def __init__(self, db_interface: DbInterface):
        self.current_state: bool = False
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

    def setup(self):
        """
        No implementation is necessary for simulation.
        """
        pass

    def turn_on(self, effective_temperature: float = 0.0, reason=""):
        """
        Simulates turning on the device connected to the power relay.
        """
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
                f"RelayControllerSim::turn_on failed to set device status to True, exception:{str(e)}"
            )
            return False

    def turn_off(self, effective_temperature: float = 0.0, reason=""):
        """
        Simulates turning off the device connected to the power relay.
        """
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
                f"RelayControllerSim::turn_off failed to set device status to False, exception:{str(e)}"
            )
            return False


if __name__ == "__main__":
    db_api = DbInterface()
    controller = RelayControllerSim(db_interface=db_api)
    assert (
        controller.current_state == False
    ), "Failed, Expected initial state to be False"

    ## test turn_on method
    controller.turn_on()
    assert (
        controller.current_state == True
    ), "RelayControllerSim failed to turn on device"
    assert (
        controller.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
        == DeviceStatus.ON.value
    ), "RelayControllerSim failed to turn on device"

    ## test turn_off method
    controller.turn_off()
    assert (
        controller.current_state == False
    ), "RelayControllerSim failed to turn off device"
    assert (
        controller.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
        == DeviceStatus.OFF.value
    ), "RelayControllerSim failed to turn off device"

    print("RelayControllerSim class: all unit tests passed")
