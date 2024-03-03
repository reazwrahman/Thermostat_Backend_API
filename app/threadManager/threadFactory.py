from app.threadManager.powerCycleThread import PowerCycleThread
from app.threadManager.heaterControllerThread import HeaterControllerThread
from app.threadManager.TemperatureSensorThread import TemperatureSensorThread 
from app.threadManager.ThermoStatThread import ThermoStatThread


## use this class below to get or kill new threads
class ThreadFactory(object):
    ## key: Type, instance
    thread_map = {
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

    @staticmethod
    def get_thread_instance(thread_name, **kwargs):
        print (f"thread map =  {ThreadFactory.thread_map}")
        if ThreadFactory.thread_map[thread_name]["instance"] == None:
            thread_instance = ThreadFactory.thread_map[thread_name]["type"](
                thread_name, **kwargs
            )
            ThreadFactory.thread_map[thread_name]["instance"] = thread_instance
        return ThreadFactory.thread_map[thread_name]["instance"]
        

    @staticmethod
    def is_thread_active(thread_name):
        return ThreadFactory.thread_map[thread_name]["instance"] != None

    @staticmethod
    def kill_thread(thread_name):
        instance = ThreadFactory.thread_map[thread_name]["instance"]
        if instance:
            instance.keep_me_alive = False
            instance.terminate()
            while instance.is_alive():
                print(f"trying to kill {thread_name}")
            ThreadFactory.thread_map[thread_name]["instance"] = None

        print(f"finished killing {thread_name}")
        return True
