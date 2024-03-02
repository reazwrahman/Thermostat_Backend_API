import json
import logging
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))

from Sensors.TemperatureSensor import TemperatureSensor

logger = logging.getLogger(__name__)


CONFIG_FILE = os.path.join(script_dir, "simulation_parameters.json")


class TemperatureSensorSim(TemperatureSensor):
    """
    This class simulates the values from a temperature sensor.
    It uses a starting temperaure in celsius, a drop rate in temperature
    (assuming it's winter) and a rise rate in temperature which will only kick
    in if the heater device is on.
    """

    def __init__(self):
        self.start_temp: float = None  # in celsius
        self.drop_rate: float = None  # how much the temp drops per second in winter
        self.rise_rate: float = (
            None  # how much the temp will rise per second if the heater is on
        )

        self.__last_read_value: float = None
        self.__read_input_file()

    def __read_input_file(self):
        """
        Reads a user defined text file to set the starting temperature,
        drop rate per second, and rise rate per second
        """
        try:
            with open(CONFIG_FILE, "r") as file:
                config_data: dict = json.load(file)
        except Exception as e:
            logger.error(
                f"TemperatureSensorSim::__read_input_file failed to read file: {CONFIG_FILE}, exception: {str(e)}"
            )
            sys.exit()

        try:
            self.start_temp = float(config_data.get("start_temp"))
            self.drop_rate = float(config_data.get("drop_rate"))
            self.rise_rate = float(config_data.get("rise_rate"))
        except Exception as e:
            logger.error(
                f"An error occured while trying to read simulation parameters, recheck the data types. Exception details: {str(e)}"
            )
            sys.exit()

    def get_temperature(self, device_status: bool):
        """
        returns the current (simulated) temperature
        """

        if self.__last_read_value == None:
            self.__last_read_value = self.start_temp
            return self.__last_read_value

        heater_is_on: bool = device_status

        if heater_is_on:
            self.__last_read_value = round(self.__last_read_value + self.rise_rate, 2)
            return self.__last_read_value
        else:
            self.__last_read_value = round(self.__last_read_value - self.drop_rate, 2)
            return self.__last_read_value


if __name__ == "__main__":
    sensor_sim = TemperatureSensorSim()

    ## test constructor/read_input_file method
    assert sensor_sim.start_temp != None, "Failed to read config data"
    assert sensor_sim.drop_rate != None, "Failed to read config data"
    assert sensor_sim.rise_rate != None, "Failed to read config data"

    # test get_temperature method::test three reads when heater is off
    i = 0
    while i < 3:
        time.sleep(0.1)
        expected_temperature: float = round(
            sensor_sim.start_temp - sensor_sim.drop_rate * i, 2
        )
        actual_temperature = sensor_sim.get_temperature(False)
        assert (
            actual_temperature == expected_temperature
        ), f"Returned wrong temperature value for read {i} (when heater is off)"
        i += 1

    ## test get_temperature method::test three reads when heater is on
    current_temperature = sensor_sim.get_temperature(True)
    i = 1
    while i < 5:
        time.sleep(0.1)
        expected_temperature = round(current_temperature + sensor_sim.rise_rate * i, 2)
        actual_temperature = sensor_sim.get_temperature(True)
        assert (
            actual_temperature == expected_temperature
        ), f"Returned wrong temperature value for read {i} (when heater is on)"
        i += 1

    print("TemperatureSensorSim class: all unit tests passed")
