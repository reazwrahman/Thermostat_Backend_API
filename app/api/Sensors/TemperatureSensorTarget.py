import datetime
import os
import sys
import logging

try:
    import Adafruit_DHT
except:
    print(f"couldnt import Adafruit_DHT, if not on a laptop something is wrong")


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))

from Sensors.TemperatureSensor import TemperatureSensor
from Config import SENSOR_PIN

logger = logging.getLogger(__name__)


class TemperatureSensorTarget(TemperatureSensor):
    """
    Actual temperature sensor class
    that will read value from the physical sensor
    """

    def __init__(self):
        super().__init__()
        self.dht_pin = SENSOR_PIN
        self.humidity = None
        self.temperature = None

        self.__last_read_temperature: float = None
        self.__last_read_humidity: float = None

    def get_temperature(self, device_status: bool = False):
        ## device status doesn't really matter for the target version of the sensor
        try:
            self.sensor = Adafruit_DHT.DHT22
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.dht_pin)
            self.__last_read_humidity = round(humidity, 2)
            self.__last_read_temperature = round(temperature, 2)

            return self.__last_read_temperature

        except Exception as e:
            logger.warn(
                f"TemperatureSensorTarget::get_temperature exception occured: {e}"
            )
            return None

    def get_humidity(self):
        return self.__last_read_humidity


if __name__ == "__main__":
    sensor = TemperatureSensorTarget()
    temp: float = sensor.get_temperature()
    humidity = sensor.get_humidity()
    print(f"temperature = {temp}, humidity = {humidity}")
    assert type(temp) == float
    print("TemperatureSensor Target Unit test passed")
