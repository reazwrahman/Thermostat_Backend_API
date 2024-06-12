import os
from threading import Thread
import sys
import click
import logging 
from flask_cors import CORS


from app.api.DatabaseAccess.DbTables import DbTables
from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.Registration.Registrar import Registrar
from app.threadManager.threadFactory import ThreadFactory   
from app.api.Config import TEMP_SENSOR_THREAD
import LoggingConfig
from app import create_app 

STATE_CHANGE_LOGGER = "state_transition_record.txt" 
STATE_RECORD_JSON = "state_transition_records_json.json"
DATABASE = "DeviceHistory.db" 

files_to_delete_at_start = [STATE_CHANGE_LOGGER, STATE_RECORD_JSON, DATABASE]


logger = logging.getLogger(__name__)


thread_factory = ThreadFactory()
app = create_app(os.getenv("FLASK_CONFIG") or "default") 
CORS(app)

registrar = Registrar()


def app_wrapper():
    app.run(host="0.0.0.0", port=8080, use_reloader=False)


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


# if __name__ == "__main__":
## clean up directory
files_deleted = True
for each in files_to_delete_at_start: 
    files_deleted &= delete_file(each)

logger.info(f"application.py all files deleted = {files_deleted}")

## prepare database
table_creator = DbTables()
table_creator.create_shared_data_table()
db_api = DbInterface()


temeprature_sensor_thread = thread_factory.get_thread_instance(
    TEMP_SENSOR_THREAD, db_interface=db_api
)

main_thread = Thread(target=app_wrapper, name="flask_app")

temeprature_sensor_thread.start()
main_thread.start()

main_thread.join()
temeprature_sensor_thread.join() 

