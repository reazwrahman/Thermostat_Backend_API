from threading import Thread    
import time

from app.api.thermoStat import ThermoStat 

class ThermoThread(Thread):  
    def __init__(self, thread_name):  
        Thread.__init__(self)
        self.thermo_stat = ThermoStat() 
        self.thread_name = thread_name 
        self.keep_me_alive = True 

    def run(self): 
        while self.keep_me_alive:
            self.thermo_stat.read_sensor_in_loop() 
            time.sleep(1) 
    
    def terminate(self): 
        pass # nothing to do
    