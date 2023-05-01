import datetime

## static members only
class DeviceHistory(object): 
    is_on = False
    last_turned_on:datetime.datetime = None # datetime object
    last_turned_off:datetime.datetime = None #datetime object 
    
    last_temperature:float = None 
    last_humidity:float = None 
