import time

from app.threadManager.powerCycleThread import PowerCycleThread
from app.threadManager.heaterControllerThread import HeaterControllerThread
from app.threadManager.TemperatureSensorThread import TemperatureSensorThread
from app.threadManager.ThermoStatThread import ThermoStatThread


## use this class below to get or kill new threads
class ThreadFactory:
    """ 
    Singleton class, used for accessing all threads
    """ 
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        self.thread_map = {
            "power_cycle": {"type": PowerCycleThread, "instance": None},
            "heater_control": {"type": HeaterControllerThread, "instance": None},
            "temperature_sensor_thread": {
                "type": TemperatureSensorThread,
                "instance": None,
            },
            "thermo_thread": {
                "type": ThermoStatThread,
                "instance": None,
            },
        }

    def get_thread_instance(self, thread_name:str, **kwargs):
        if self.thread_map[thread_name]["instance"] == None:
            thread_instance = self.thread_map[thread_name]["type"](
                thread_name, **kwargs
            )
            self.thread_map[thread_name]["instance"] = thread_instance
        return self.thread_map[thread_name]["instance"]

    def is_thread_active(self, thread_name:str):
        return self.thread_map[thread_name]["instance"] != None

    def kill_thread(self, thread_name):
        instance = self.thread_map[thread_name]["instance"]
        if instance:
            instance.keep_me_alive = False
            instance.terminate()
            print(f"trying to kill {thread_name}", end=" ")
            while instance.is_alive():
                print(".", end="")
                time.sleep(3)
            self.thread_map[thread_name]["instance"] = None

        print(f"finished killing {thread_name}")
        return True
