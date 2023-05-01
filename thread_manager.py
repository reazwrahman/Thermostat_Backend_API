from threading import Thread  
from app.api.thermoStat import ThermoStat  
from app.api.powerCycle import PowerCycle 
import time


class ThermoThread(Thread): 
    def __init__(self, thread_name):  
        Thread.__init__(self)
        self.thermo_stat = ThermoStat() 
        self.thread_name = thread_name 
        self.keep_me_alive = True 

    def run(self): 
        while self.keep_me_alive:  
            print('hello hi')
            self.thermo_stat.read_sensor_in_loop()
    
    def get_temperature(self): 
        return self.thermo_stat.get_temperature() 

    def get_humidity(self): 
        return self.thermo_stat.get_humidity() 


class PowerCycleThread(Thread): 
    def __init__(self, thread_name, **kwargs):  
        Thread.__init__(self)  
        print(kwargs)
        if "power_off_minutes" not in kwargs or "power_on_minutes" not in kwargs: 
            raise ValueError ('PowerCycleThread::__init__ can not start cycle without valid power on and power off minutes')
        
        power_on_minutes = kwargs["power_on_minutes"]  
        power_off_minutes = kwargs["power_off_minutes"]
        
        self.power_cycle = PowerCycle(power_on_minutes, power_off_minutes) 
        self.thread_name = thread_name 
        self.keep_me_alive = True 
    
    def set_thread_parameters(self, power_on_minutes, power_off_minutes):  
        self.power_cycle.set_cycle_times(power_on_minutes, power_off_minutes)

    
    def run(self):
        while self.keep_me_alive: 
            self.power_cycle.execute_state_machine()
    
    def get_power_cycle(self):
        return self.power_cycle


## use this class below to get or kill new threads
class ThreadFactory(object):  
                ## key: Type, instance
    thread_map ={"thermostat": { "type": ThermoThread, 
                                "instance": None}, 
                 "power_cycle": { "type": PowerCycleThread, 
                                "instance": None}
                 } 
     
    
    @staticmethod  
    def get_thread_instance(thread_name, **kwargs):
        if ThreadFactory.thread_map[thread_name]["instance"] == None: 
            thread_instance = ThreadFactory.thread_map[thread_name]["type"](thread_name,**kwargs)
            ThreadFactory.thread_map[thread_name]["instance"] = thread_instance
            return thread_instance 
    

    @staticmethod 
    def is_thread_active(thread_name): 
        return ThreadFactory.thread_map[thread_name]["instance"] != None   
    

    @staticmethod 
    def kill_thread(thread_name): 
        instance = ThreadFactory.thread_map[thread_name]["instance"] 
        if instance: 
            instance.keep_me_alive = False 
            while instance.is_alive(): 
                print(F'trying to kill {thread_name}')
            ThreadFactory.thread_map[thread_name]["instance"] = None
        
        print(f'finished killing {thread_name}') 
        return True