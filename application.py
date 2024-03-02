import os
from threading import Thread
import sys
import click
import logging


from app.api.DatabaseAccess.DbTables import DbTables
from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.Registration.Registrar import Registrar, RunningModes
from app.api.Sensors.TemperatureSensorSim import TemperatureSensorSim
from app.api.Sensors.TemperatureSensorTarget import TemperatureSensorTarget
from app.api.Relays.RelayControllerSim import RelayControllerSim
from app.api.Relays.RelayControllerTarget import RelayControllerTarget
from app.threadManager.threadFactory import ThreadFactory
from app import create_app

STATE_CHANGE_LOGGER = "state_transition_record.txt"
DATABASE = "DeviceHistory.db"

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

app = create_app(os.getenv("FLASK_CONFIG") or "default")


def app_wrapper():
    app.run(host="0.0.0.0", port=80, use_reloader=False)


def get_target_temperature():
    """
    gets desired temperature from user input
    """
    input_is_invalid: bool = True
    while input_is_invalid:
        try:
            target_temp = input(
                "Please enter the desired temperature in Celsius (between 0 and 50): "
            )
            target_temp = float(target_temp)
            if target_temp < 0 or target_temp > 50:
                raise ValueError
            input_is_invalid = False
        except ValueError:
            print(
                "Entered value is either not convertible to a number or outside of the 0 to 50 range"
            )

        except Exception as e:
            print(f"Unknown exception occured, exception: {str(e)}")

    return target_temp


def delete_file(file_name):
    """
    deletes the specified file
    """
    try:
        if os.path.exists(os.path.join(os.getcwd(), file_name)):
            os.remove(file_name)
            logger.info(f"{file_name} deleted")
        return True
    except Exception as e:
        logger.error(f"Unable to delete file {file_name}, exception: {str(e)}")
        return False


#if __name__ == "__main__":
## clean up directory
files_deleted = delete_file(STATE_CHANGE_LOGGER) and delete_file(DATABASE)

## prepare database
table_creator = DbTables()
table_creator.create_shared_data_table()
db_api = DbInterface()

## register all sensors
simulation_sensor = TemperatureSensorSim()
target_sensor = TemperatureSensorTarget()
Registrar.register_temperature_sensor(simulation_sensor, RunningModes.SIM)
Registrar.register_temperature_sensor(target_sensor, RunningModes.TARGET)

## register all relay controllers
simulation_relay = RelayControllerSim(db_interface=db_api)
target_relay = RelayControllerTarget()
Registrar.register_relay_controllers(simulation_relay, RunningModes.SIM)
Registrar.register_relay_controllers(target_relay, RunningModes.TARGET) 
Registrar.get_relay_controllers(RunningModes.SIM)

# thermo_thread = ThreadFactory.get_thread_instance("thermostat")
# thermo_thread.start()
temeprature_sensor_thread = ThreadFactory.get_thread_instance(
    "temperature_sensor_thread", db_interface=db_api
) 
print('application calling thermo')
relay = Registrar.get_relay_controllers(RunningModes.SIM)
thermo_thread = ThreadFactory.get_thread_instance("thermo_thread",target_temperature=22.2, db_interface=db_api)

main_thread = Thread(target=app_wrapper, name="flask_app")

temeprature_sensor_thread.start()
main_thread.start()

main_thread.join()
temeprature_sensor_thread.join()
