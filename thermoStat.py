try:
    import Adafruit_DHT 
except: 
    print (f'couldnt import Adafruit_DHT, if not on a laptop something is wrong') 

class ThermoStat(object):
    def __init__(self): 
        self.dht_pin = 4  
        self.humidity = None 
        self.temperature = None
    
    def read_sensor(self):  
        try:  
            self.sensor = Adafruit_DHT.DHT22
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.dht_pin) 
            self.humidity = round(humidity, 3) 
            self.temperature = round(temperature, 3)   
            print(humidity) 
            print(temperature)
        except Exception as e:
            print(e)


    def get_temperature(self):
        return self.temperature 
    
    def get_humidity(self): 
        return self.humidity