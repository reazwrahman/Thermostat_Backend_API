import sqlite3
import logging
from enum import Enum

DB_NAME = "DeviceHistory.db"
SHARED_DATA_TABLE = "SharedData"

logger = logging.getLogger(__name__)


class SharedDataColumns(Enum):
    ID = "id"
    DEVICE_STATUS = "device_status"
    LAST_TEMPERATURE = "last_temperature"
    LAST_TURNED_ON = "last_turned_on"
    LAST_TURNED_OFF = "last_turned_off"
    TARGET_TEMPERATURE = "target_temperature"


class DbTables:
    """
    Represents the tables in the Databse. Responsible for creating tables.
    """

    def __init__(self):
        self.db_name = DB_NAME

    def create_shared_data_table(self):
        """
        Creates a table with the shared data between threads
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {SHARED_DATA_TABLE} (
                    {SharedDataColumns.ID.value} INTEGER PRIMARY KEY, 
                    {SharedDataColumns.DEVICE_STATUS.value} TEXT,
                    {SharedDataColumns.LAST_TEMPERATURE.value} REAL,
                    {SharedDataColumns.LAST_TURNED_ON.value} TEXT,
                    {SharedDataColumns.LAST_TURNED_OFF.value} TEXT,
                    {SharedDataColumns.TARGET_TEMPERATURE.value} REAL
                )
            """
            )

            insert_query = f"""
            INSERT INTO {SHARED_DATA_TABLE} ({SharedDataColumns.ID.value}, {SharedDataColumns.DEVICE_STATUS.value}, {SharedDataColumns.LAST_TEMPERATURE.value}, 
            {SharedDataColumns.LAST_TURNED_ON.value}, {SharedDataColumns.LAST_TURNED_OFF.value}, {SharedDataColumns.TARGET_TEMPERATURE.value})
            VALUES ('1', 'OFF', NULL, NULL, NULL, NULL)"""
            cursor.execute(insert_query)
            conn.commit()
            logger.info(f"Table {SHARED_DATA_TABLE} created successfully.")

        except sqlite3.Error as e:
            logger.info("Error creating table:", e)

        finally:
            if conn:
                conn.close()
