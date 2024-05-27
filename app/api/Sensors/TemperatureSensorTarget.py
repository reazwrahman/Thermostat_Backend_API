import datetime 
import os 
import sys

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


class TemperatureSensorTarget(TemperatureSensor):
    """
    Actual temperature sensor class
    that will read value from the physical sensor
    """

    def __init__(self):
        super().__init__() 
        self.dht_pin = 4 
        self.humidity = None
        self.temperature = None

       
        self.__last_read_value: tuple = None

    def get_temperature(self):
        try:
            self.sensor = Adafruit_DHT.DHT22
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.dht_pin)
            self.humidity = round(humidity, 2)
            self.temperature = round(temperature, 2) 

            self.__last_read_value = (self.humidity, self.temperature)     
            return self.__last_read_value 
        
        except Exception as e:
            print(f"TemperatureSensorTarget::get_temperature exception occured: {e}")


if __name__ == "__main__": 
    sensor = TemperatureSensorTarget()
    reading:tuple = sensor.get_temperature() 
    assert(type(reading[0]) == float and type(reading[1]) == float)