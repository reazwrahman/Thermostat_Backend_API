""" 
outdated file. 
keeping just for reference for now


import datetime
from enum import Enum

from app.api.pinController import PinController
from app.api.device_history import DeviceHistory


class PowerState(Enum):
    NOT_STARTED = 1
    ON = 2
    OFF = 3


class PowerCycle(object):
    def __init__(self, power_on_minutes, power_off_minutes):
        self.power_on_minutes: int = power_on_minutes
        self.power_off_minutes: int = power_off_minutes
        self.current_state: PowerState = PowerState.NOT_STARTED
        self.turned_on_time: datetime = None
        self.turned_off_time: datetime = None

        self.pin_controller = PinController()

    def update_cycle_times(self, power_on_time, power_off_time):
        self.power_on_minutes = power_on_time
        self.power_off_minutes = power_off_time

    def execute_state_machine(self):
        if self.current_state == PowerState.NOT_STARTED:
            self.__start_power_cycle__()

        elif self.current_state == PowerState.ON:
            self.__execute_on_state__()

        elif self.current_state == PowerState.OFF:
            self.__execute_off_state__()

    def terminate(self):
        # turn device off, if it's on
        if DeviceHistory.is_on:
            self.pin_controller.turn_off()
            DeviceHistory.is_on = False
            DeviceHistory.last_turned_off = datetime.datetime.now()
            self.turned_off_time = datetime.datetime.now()

    def __start_power_cycle__(self):
        # start the cycle
        print("====================================================")
        print("PowerCycle:: starting power cycle")
        print("====================================================")

        if DeviceHistory.is_on:  # if device was already on
            self.turned_on_time = DeviceHistory.last_turned_on
            print("somehow it was already on")
        else:
            self.pin_controller.turn_on()
            DeviceHistory.is_on = True
            print("turning on now")
            DeviceHistory.last_turned_on = datetime.datetime.now()
            self.turned_on_time = DeviceHistory.last_turned_on

        self.current_state = PowerState.ON
        print("====================================================")
        print(f"PowerCycle:: device turned on at {self.turned_on_time}")
        print("====================================================")

    def __execute_on_state__(self):
        time_now = datetime.datetime.now()
        timedelta = time_now - self.turned_on_time
        delta_in_minutes = int(timedelta.total_seconds() / 60)
        print(f"PowerCycle:: executing on state delta is {timedelta}")

        ## time to start off cycle
        if delta_in_minutes >= self.power_on_minutes:
            if DeviceHistory.is_on:
                self.pin_controller.turn_off()
                DeviceHistory.is_on = False
                DeviceHistory.last_turned_off = datetime.datetime.now()
                self.turned_off_time = datetime.datetime.now()

            else:  # if device is already off (manually perhaps?)
                self.turned_off_time = DeviceHistory.last_turned_off

            self.current_state = PowerState.OFF
            print("====================================================")
            print(f"PowerCycle:: device turned off at {self.turned_off_time}")
            print("====================================================")

    def __execute_off_state__(self):
        time_now = datetime.datetime.now()
        timedelta = time_now - self.turned_off_time
        delta_in_minutes = int(timedelta.total_seconds() / 60)
        print(f"PowerCycle:: executing off state delta is {timedelta}")

        ## time to start on cycle
        if delta_in_minutes >= self.power_off_minutes:
            if DeviceHistory.is_on:  # if device is already on (manually perhaps?)
                self.turned_on_time = DeviceHistory.last_turned_on

            else:
                self.pin_controller.turn_on()
                DeviceHistory.is_on = True
                DeviceHistory.last_turned_on = datetime.datetime.now()
                self.turned_on_time = datetime.datetime.now()

            self.current_state = PowerState.ON
            print("====================================================")
            print(f"PowerCycle:: device turned on at {self.turned_on_time}")
            print("====================================================")

            
"""
