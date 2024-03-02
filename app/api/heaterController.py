import datetime
from enum import Enum

from app.api.pinController import PinController
from app.api.device_history import DeviceHistory
import app.api.device_history

path = app.api.device_history
from app.api.operationalConstants import OperationalConstants


class PowerStates(Enum):
    NOT_STARTED = 1
    ON_STATE = 2
    COOL_DOWN = 3


## state machine diagram showing the different state transitions:
#            ___________________
#           |                   |
#           x                   |
## NOT_STARTED  --> ON  --> COOL_DOWN
#               |              ^
#               |              |
#                --------------


class HeaterController(object):
    def __init__(self, target_temp):
        self.cool_down_period = OperationalConstants.heater_cool_down  # minutes
        self.min_on_time = OperationalConstants.heater_min_on_time
        self.max_on_time = OperationalConstants.heater_max_on_time

        self.last_turned_on_time: datetime = None
        self.cool_down_started_time: datetime = None

        self.pin_controller = PinController()
        self.current_state = PowerStates.NOT_STARTED
        self.target_temp = target_temp

    def update_target_temp(self, target_temp):
        self.target_temp = target_temp

    def execute_state_machine(self):
        current_temp = DeviceHistory.last_temperature
        print(current_temp)

        if self.current_state == PowerStates.NOT_STARTED:
            self.__start_state_machine__()

        elif self.current_state == PowerStates.ON_STATE:
            self.__execute_on_state__()

        elif self.current_state == PowerStates.COOL_DOWN:
            self.__execute_cool_down_state__()

        else:
            raise ValueError("HeaterController::execute_state_machine invalid state")

    def __start_state_machine__(self):
        ## if device was already on when we started, we want to account for that
        if DeviceHistory.is_on:
            self.last_turned_on_time = DeviceHistory.last_turned_on
            self.current_state = PowerStates.ON_STATE
        else:
            current_temp = DeviceHistory.last_temperature
            ## on condition
            if self.target_temp > current_temp:
                self.pin_controller.turn_on()
                DeviceHistory.is_on = True
                self.last_turned_on_time = datetime.datetime.now()
                self.current_state = PowerStates.ON_STATE

    def __execute_on_state__(self):
        current_temp = DeviceHistory.last_temperature
        time_now = datetime.datetime.now()
        timedelta = time_now - self.last_turned_on_time
        delta_in_minutes = int(timedelta.total_seconds() / 60)

        print(f"on state delta in minutes {delta_in_minutes}")
        # we don't want to switch too quickly, if it's on let's keep it on for a minimum interval
        if delta_in_minutes >= self.min_on_time:
            # temperature changes or maximum on time exceeds, lets go on a cool down
            if current_temp >= self.target_temp or delta_in_minutes >= self.max_on_time:
                # time to switch state
                print("inside block")
                self.pin_controller.turn_off()
                DeviceHistory.is_on = False
                self.current_state = PowerStates.COOL_DOWN
                self.cool_down_started_time = datetime.datetime.now()

    def __execute_cool_down_state__(self):
        time_now = datetime.datetime.now()
        timedelta = time_now - self.cool_down_started_time
        delta_in_minutes = int(timedelta.total_seconds() / 60)

        if delta_in_minutes >= self.cool_down_period:
            self.current_state = PowerStates.NOT_STARTED

    def terminate(self):
        # turn device off, if it's on
        if DeviceHistory.is_on:
            self.pin_controller.turn_off()
            DeviceHistory.is_on = False
            DeviceHistory.last_turned_off = datetime.datetime.now()
            self.turned_off_time = datetime.datetime.now()

    def get_curent_state_details(self):
        ## we want to know what state we are in,
        ## what was last turned on time
        ## what was last cool down started time
        ## current temp, target temp
        ## elapsed time since last turned on
        ## elapsed minutes since last cool down
        # timedelta = time_now - self.last_turned_on_time
        # delta_in_minutes = int(timedelta.total_seconds() / 60)
        time_now = datetime.datetime.now()
        turn_on_delta = "None"
        cool_down_delta = "None"
        if self.last_turned_on_time:
            turn_on_delta = str(time_now - self.last_turned_on_time)
        if self.cool_down_started_time:
            cool_down_delta = str(time_now - self.cool_down_started_time)
        state = {}
        state["current_state"] = self.current_state.name
        state["current_temp"] = DeviceHistory.last_temperature
        state["target_temp"] = self.target_temp
        state["time_since_last_turn_on"] = turn_on_delta
        state["time_since_last_cool_down"] = cool_down_delta
        state["cool_down_period"] = self.cool_down_period
        state["min_heater_on_time"] = self.min_on_time
        state["max_heater_on_time"] = self.max_on_time
        return state
