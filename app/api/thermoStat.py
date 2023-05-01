import datetime
try:
    import Adafruit_DHT 
except: 
    print (f'couldnt import Adafruit_DHT, if not on a laptop something is wrong') 

class ThermoStat(object):
    def __init__(self, run_in_loop = False): 
        self.dht_pin = 4  
        self.humidity = None 
        self.temperature = None
        
        ## optional, needed to run as a thread 
        self.wait_for = 5 # minutes before reading new sets of data 
        self.sample_size = 5 # take average of last 5 valid data points
        self.last_read:datetime = None
    
    def read_sensor(self):  
        try:  
            self.sensor = Adafruit_DHT.DHT22
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.dht_pin) 
            self.humidity = round(humidity, 2) 
            self.temperature = round(temperature, 2)   
            print(humidity) 
            print(temperature) 
            return humidity, temperature
        except Exception as e:
            print(e) 
    
    def read_sensor_in_loop(self):        
        time_now = datetime.datetime.now()  
        print (f'ThermoStat::read_sensor_in_loop time_now {time_now}')
        if self.last_read: 
            timedelta = time_now - self.last_read
            delta_in_minutes = int(timedelta.total_seconds() / 60)

        if not self.last_read or delta_in_minutes >= self.wait_for: 
            print (f'ThermoStat::read_sensor_in_loop time to make new reads')
            total_humidity = 0 
            total_temperature = 0 
            for i in range(self.sample_size): 
                humidity, temperature = self.read_sensor()
                if humidity and temperature:  
                    i+=1 
                    total_humidity += humidity 
                    total_temperature += temperature  
    

            self.temperature = (total_temperature / self.sample_size) 
            self.humidity = (total_humidity / self.sample_size) 
            print (f'ThermoStat::read_sensor_in_loop avg humidity and temperature = {self.humidity} , {self.temperature}')
            self.last_read = datetime.datetime.now()


    def get_temperature(self):
        return self.temperature 
    
    def get_humidity(self):
        return self.humidity