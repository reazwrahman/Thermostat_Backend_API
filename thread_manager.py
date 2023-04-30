from threading import Thread  
from app.api.thermoStat import ThermoStat 

class ThermoThread(Thread): 
    thermostat_started = False 

    def __init__(self, thread_name):  
        Thread.__init__(self)
        self.thermo_stat = ThermoStat() 
        self.thread_name = thread_name

    def run(self): 
        while True: 
            self.thermo_stat.read_sensor()
    
    def get_thermostat(self): 
        return self.thermo_stat
        

thermo_thread = ThermoThread("read_sensor_thread")