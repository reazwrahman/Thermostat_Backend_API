import os
import sys
import logging
import datetime
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.Utility import Utility
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.DatabaseAccess.DbInterface import DbInterface
from api.Relays.RelayController import RelayController
from api.Config import DeviceStatus
from api.Registration.Registrar import Registrar
from api.Config import RUNNING_MODE

logger = logging.getLogger(__name__)


class States(Enum):
    ALREADY_ON = "ALREADY_ON"
    ALREADY_OFF = "ALREADY_OFF"
    TURNED_ON = "TURNED_ON"
    TURNED_OFF = "TURNED_OFF"
    REQUEST_DENIED = "REQUEST_DENIED"
    NO_ACTION = "NO_ACTION"


class PowerControlGateKeeper:
    """
    This class is responsible for ensuring that it's safe to turn on or
    turn off the device, based on the safety parameters
    outlined in the configs.
    """

    def __init__(self, db_interface: DbInterface):
        self.registrar = Registrar()
        self.relay_controller: RelayController = self.registrar.get_relay_controllers(
            RUNNING_MODE.value
        )
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

    def turn_on(self, effective_temperature=0.0, reason="") -> States:
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """
        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.ON.value
        ):
            message = "PowerControlGateKeeper::turn_on, device is already on, nothing to do here"
            logger.info(message)
            return States.ALREADY_ON

        last_turned_off: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_OFF.value
        )
        if not last_turned_off:
            self.relay_controller.turn_on(effective_temperature, reason=reason)
            return States.TURNED_ON

        time_difference = self.utility.get_time_delta(last_turned_off)
        cool_down_period: int = self.db_interface.read_column(
            SharedDataColumns.COOLDOWN_PERIOD.value
        )

        if time_difference >= cool_down_period:
            self.relay_controller.turn_on(effective_temperature, reason=reason)
            logger.warn("PowerControlGateKeeper::turn_on turning device on")
            return States.TURNED_ON

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_on Unable to turn device on, device is currently in a cool down stage"
            )
            return States.REQUEST_DENIED

    def turn_off(self, effective_temperature=0.0, reason="") -> States:
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """
        successful_log_msg = "PowerControlGateKeeper::turn_off turning device off"

        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.OFF.value
        ):
            logger.info(
                "PowerControlGateKeeper::turn_off, device is already off, nothing to do here"
            )
            return States.ALREADY_OFF

        last_turned_on: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_ON.value
        )
        if not last_turned_on:
            self.relay_controller.turn_off(effective_temperature, reason=reason)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        time_difference = self.utility.get_time_delta(last_turned_on)

        minimum_on_time = self.db_interface.read_column(
            SharedDataColumns.MINIMUM_ON_TIME.value
        )

        if time_difference >= minimum_on_time:
            self.relay_controller.turn_off(effective_temperature, reason=reason)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_off Unable to turn device off, device needs to be on for a minimum period of time"
            )
            return States.REQUEST_DENIED

    def forced_turn_on(self, effective_temperature=0.0, reason="") -> States:
        """
        turn on without any decioning
        """
        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.ON.value
        ):
            message = "PowerControlGateKeeper::turn_on, device is already on, nothing to do here"
            logger.info(message)
            return States.ALREADY_ON

        else:
            self.relay_controller.turn_on(effective_temperature, reason=reason)
            logger.warn("PowerControlGateKeeper::turn_on turning device on")
            return States.TURNED_ON

    def forced_turn_off(self, effective_temperature=0.0, reason="") -> States:
        """
        turn off without any decioning
        """
        successful_log_msg = "PowerControlGateKeeper::turn_off turning device off"

        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.OFF.value
        ):
            logger.info(
                "PowerControlGateKeeper::turn_off, device is already off, nothing to do here"
            )
            return States.ALREADY_OFF

        else:
            self.relay_controller.turn_off(effective_temperature, reason=reason)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF
