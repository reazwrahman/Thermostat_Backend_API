from api.Sensors.TemperatureSensor import TemperatureSensor


class TemperatureSensorTarget(TemperatureSensor):
    """
    Actual temperature sensor class
    that will read value from the physical sensor
    """

    def __init__(self):
        super().__init__()

    def get_temperature(self):
        return super().get_temperature()
