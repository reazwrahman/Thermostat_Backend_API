""" 
outdated file. 
keeping just for reference for now
"""

import datetime


## static members only
class DeviceHistory(object):
    is_on = False
    last_turned_on: datetime.datetime = None  # datetime object
    last_turned_off: datetime.datetime = None  # datetime object

    last_temperature: float = 23
    last_humidity: float = None
