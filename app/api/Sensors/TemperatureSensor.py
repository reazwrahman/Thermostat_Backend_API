class TemperatureSensor:
    """
    Abstract base class. Used as a blueprint only.
    """

    def __init__(self):
        pass

    def get_temperature(self):
        raise NotImplementedError 
    
    def get_humidity(self): 
        raise NotImplementedError 
