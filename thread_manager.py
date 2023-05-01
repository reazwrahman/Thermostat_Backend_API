from threading import Thread  
from app.api.thermoStat import ThermoStat  
from app.api.powerCycle import PowerCycle 
import time

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


class PowerCycleThread(Thread): 
    thread_started = False 

    def __init__(self, thread_name, power_on_minutes, power_off_minutes):  
        Thread.__init__(self)
        self.power_cycle = PowerCycle(power_on_minutes, power_off_minutes) 
        self.thread_name = thread_name 
        self.keep_me_alive = True
    
    def run(self):
        while self.keep_me_alive: 
            self.power_cycle.execute_state_machine()  
            time.sleep(1)
    
    def get_power_cycle(self):
        return self.power_cycle



## create instances of the threads, these will be started and stopped by the program at run time
#thermo_thread = ThermoThread("read_sensor_thread") 
#power_cycle_thread = PowerCycleThread("cycle_power", 1, 1) 

class ThreadFactory(object):  
                ## key: Type, instance
    thread_map ={"thermostat": { "type": ThermoThread, 
                                "instance": None}, 
                 "power_cycle": { "type": PowerCycleThread, 
                                "instance": None}
                 } 
    
    @staticmethod  
    def get_power_cycle_thread(power_on_minutes, power_off_minutes):
        if ThreadFactory.thread_map["power_cycle"]["instance"] == None: 
            power_cycle_thread = PowerCycleThread("power_cycle", power_on_minutes, power_off_minutes)  
            ThreadFactory.thread_map["power_cycle"]["instance"] = power_cycle_thread 
            return power_cycle_thread

    @staticmethod 
    def kill_power_cycle_thread(): 
        instance = ThreadFactory.thread_map["power_cycle"]["instance"] 
        if instance: 
            instance.keep_me_alive = False 
            while instance.is_alive(): 
                print('trying to kill power cycle')
            ThreadFactory.thread_map["power_cycle"]["instance"] = None
        
        print('finished killing') 
        return  
    
    @staticmethod 
    def is_power_cycle_active(): 
        return ThreadFactory.thread_map["power_cycle"]["instance"] != None 