try:
    import RPi.GPIO as GPIO 
except: 
    print (f'couldnt import RPi, if not on a laptop something is wrong') 

from app.api.operationalConstants import OperationalConstants

class PinController(object):
    def __init__(self, pin = OperationalConstants.led_pin): 
        self.pin = pin  
        self.__setup__() 
    
    def __setup__(self):  
        try:
            GPIO.setwarnings(False) # Ignore warning for now
            GPIO.setmode(GPIO.BCM) 
            GPIO.setup(self.pin, GPIO.OUT)  
        except Exception as e:
            print(e)

    def turn_on(self):  
        try:  
            GPIO.output(self.pin, GPIO.HIGH)
            return True 
        except Exception as e:
            print(e) 
            return False


    def turn_off(self):
        try:  
            GPIO.output(self.pin, GPIO.LOW)  
            return True 
        except Exception as e:
            print(e) 
            return False 
    