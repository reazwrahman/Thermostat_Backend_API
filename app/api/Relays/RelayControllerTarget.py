from api.Relays.RelayController import RelayController


class RelayControllerTarget(RelayController):
    """
    Actual relay controller class that will interact with the hardware
    relay device to turn on/off the connected device.
    """

    def __init__(self):
        pass

    def setup(self):
        raise NotImplementedError

    def turn_on(self):
        raise NotImplementedError

    def turn_off(self):
        raise NotImplementedError
