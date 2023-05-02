import datetime 
from enum import Enum  

from app.api.pinController import PinController 
from app.api.device_history import DeviceHistory

class PowerStates(Enum):
    NOT_STARTED = 1
    ON_STATE = 2
    OFF_STATE = 3  
    COOL_DOWN = 4

## state machine diagram showing the different state transitions: 
#         ____________________
#        |                    |       
#        x                    |
## NOT_STARTED  --> ON  --> COOL_DOWN 
#             |     ^
#             |     |
#             ---> OFF  

class HeaterController(object):
    def __init__(self, target_temp): 
        self.cool_down_period = 10 #minutes 
        self.last_turned_on_time:datetime = None 
        self.last_turned_off_time:datetime = None 
        self.cool_down_started_time:datetime = None  

        self.pin_controller = PinController()
        self.current_state = PowerStates.NOT_STARTED 
        self.target_temp = target_temp 
    
    def update_target_temp(self, target_temp):
        self.target_temp = target_temp
    
    def execute_state_machine(self): 
        if self.current_state == PowerStates.NOT_STARTED:   
            self.__start_state_machine__() 

        elif self.current_state == PowerStates.ON_STATE:
            self.__execute_on_state__()  
        
        elif self.current_state == PowerStates.COOL_DOWN: 
            self.__execute_cool_down_state__() 
        
        elif self.current_state == PowerStates.OFF_STATE: 
            self.execute_off_state__()

        



    def __start_state_machine__(self): 
        current_temp = DeviceHistory.last_temperature  
        ## on condition
        if self.target_temp > current_temp: 
            if DeviceHistory.is_on: 
                self.last_turned_on_time = DeviceHistory.last_turned_on 
            else:  
                self.pin_controller.turn_on()
                DeviceHistory.is_on = True
                self.last_turned_on_time = datetime.datetime.now()
            
            self.current_state = PowerStates.ON_STATE 
        
        ## off condition
        else: 
            if DeviceHistory.is_on: 
                self.pin_controller.turn_off()  
                DeviceHistory.is_on = False
                self.last_turned_off_time = datetime.datetime.now() 
            else: 
                self.last_turned_off_time = DeviceHistory.last_turned_off 

            self.current_state = PowerStates.OFF_STATE 
 
    
    def __execute_on_state__(self): 
        current_temp = DeviceHistory.last_temperature 
        time_now = datetime.datetime.now()
        timedelta = time_now - self.last_turned_on_time
        delta_in_minutes = int(timedelta.total_seconds() / 60) 


        if current_temp >= self.target_temp or delta_in_minutes > 30:  
            # time to switch state 
            self.pin_controller.turn_off()  
            DeviceHistory.is_on = False 
            self.current_state = PowerStates.COOL_DOWN  
            self.cool_down_started_time = datetime.datetime.now() 
        
        else: 
            pass # keep chilling in this state

    
    def __execute_cool_down_state__(self): 
        time_now = datetime.datetime.now()
        timedelta = time_now - self.last_turned_on_time
        delta_in_minutes = int(timedelta.total_seconds() / 60)  

        if delta_in_minutes > self.cool_down_period: 
            self.current_state = PowerStates.NOT_STARTED  
        
        else: 
            pass ## keep chilling 
    
    def __execute_off_state__(self): 
        
