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
        super().__init__(db_interface)

    def setup(self):
        """
        No implementation is necessary for simulation.
        """
        pass

    def turn_on(self, effective_temperature: float = 0.0, reason="user action"):
        """
        Simulates turning on the device connected to the power relay.
        """
        super().turn_on()

    def turn_off(self, effective_temperature: float = 0.0, reason="user action"):
        """
        Simulates turning off the device connected to the power relay.
        """
        super().turn_off()


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
