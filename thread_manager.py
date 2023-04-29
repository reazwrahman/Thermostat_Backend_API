from threading import Thread 
from thermoStat import ThermoStat 

class ThermoThreadHelper(object): 
    thermostat_started = False 

    def __init__(self): 
        self.thermo_stat = ThermoStat()

    def run_sensor(self): 
        while True: 
            self.thermo_stat.read_sensor()
    
    def get_thermostat(self): 
        return self.thermo_stat
        

thermo_thread_helper = ThermoThreadHelper()
thermo_thread = Thread(target = thermo_thread_helper.run_sensor, name='thermo_thread') 