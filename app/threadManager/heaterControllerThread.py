from threading import Thread

from app.api.heaterController import HeaterController  
import time


class HeaterControllerThread(Thread): 
    def __init__(self, thread_name, **kwargs): 
        if "target_temp" not in kwargs: 
            raise ValueError ('HeaterControllerThread::__init__ can not start thread without target temperature')  
        
        Thread.__init__(self)  

        self.heater_controller = HeaterController(kwargs["target_temp"])
        self.thread_name = thread_name 
        self.keep_me_alive = True 
    
    def run(self): 
        i=0
        while self.keep_me_alive:  
            state = self.heater_controller.get_curent_state_details() 
            print (state) 
            self.heater_controller.execute_state_machine()  
            time.sleep(4)
            i+=1 
            if i >= 7: 
                new_temp = input('enter temp: ') 
                from app.api.device_history import DeviceHistory 
                DeviceHistory.last_temperature = float(new_temp) 
                i=0
    
    def terminate(self): 
        self.heater_controller.terminate()
    
    def get_heater_controller(self):
        return self.heater_controller