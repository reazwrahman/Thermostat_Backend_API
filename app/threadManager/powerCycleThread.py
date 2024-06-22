""" 
outdated file. 
keeping just for reference for now


from threading import Thread
from app.api.powerCycle import PowerCycle


class PowerCycleThread(Thread):
    def __init__(self, thread_name, **kwargs):
        if "power_off_minutes" not in kwargs or "power_on_minutes" not in kwargs:
            raise ValueError(
                "PowerCycleThread::__init__ can not start cycle without valid power on and power off minutes"
            )

        Thread.__init__(self)

        power_on_minutes = kwargs["power_on_minutes"]
        power_off_minutes = kwargs["power_off_minutes"]

        self.power_cycle = PowerCycle(power_on_minutes, power_off_minutes)
        self.thread_name = thread_name
        self.keep_me_alive = True

    def set_thread_parameters(self, power_on_minutes, power_off_minutes):
        self.power_cycle.set_cycle_times(power_on_minutes, power_off_minutes)

    def run(self):
        while self.keep_me_alive:
            self.power_cycle.execute_state_machine()

    def terminate(self):
        self.power_cycle.terminate()

    def get_power_cycle(self):
        return self.power_cycle

"""
