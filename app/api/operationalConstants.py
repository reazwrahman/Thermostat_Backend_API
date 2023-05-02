

## static members only
class OperationalConstants(object):  
    # GPIO
    led_pin = 26 
    relay_pin = 0 # TODO 
    dht_pin = 4

    # sensor 
    sensor_reading_interval = 2 # minutes 
    sensor_sample_size = 5 # data points  

    # heater  
    heater_min_on_time = 1 # minutes
    heater_max_on_time = 1 # minutes
    heater_cool_down = 1 # minutes


