class RelayController:
    """
    Abstract base class. Used as a blueprint only.
    """

    def __init__(self):
        pass

    def setup(self):
        raise NotImplementedError

    def turn_on(self):
        raise NotImplementedError

    def turn_off(self):
        raise NotImplementedError
