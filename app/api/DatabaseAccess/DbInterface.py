import sqlite3
import logging
from enum import Enum
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from api.DatabaseAccess.DbTables import SharedDataColumns

DB_NAME = "DeviceHistory.db"
SHARED_DATA_TABLE = "SharedData"

logger = logging.getLogger(__name__)


class DbInterface:
    """
    An API to interact with the database
    """

    def __init__(self):
        self.db_name = DB_NAME

    def update_column(self, column_name, new_value):
        """
        Updates a column in the database table with the provided value
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Check if the table is empty
            cursor.execute(f"SELECT COUNT(*) FROM {SHARED_DATA_TABLE}")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    f"""
                    INSERT INTO {SHARED_DATA_TABLE} (id, {column_name})
                    VALUES (1, ?)
                """,
                    (new_value,),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE {SHARED_DATA_TABLE}
                    SET {column_name} = ?
                    WHERE id = 1
                """,
                    (new_value,),
                )

            conn.commit()
            logger.info(f"{column_name} value updated successfully: {new_value}.")

        except sqlite3.Error as e:
            logger.error(f"Error updating {column_name} value:", e)

        finally:
            if conn:
                conn.close()

    def update_multiple_columns(self, column_names, new_values):
        """
        Updates multiple columns in the database table with the provided values
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Update existing row
            set_clause = ", ".join(
                [f"{column_name} = ?" for column_name in column_names]
            )
            query = f"""
                UPDATE {SHARED_DATA_TABLE}
                SET {set_clause}
                WHERE id = 1
            """
            cursor.execute(query, new_values)

            conn.commit()
            logger.info(f"Columns updated successfully: {column_names}")

        except sqlite3.Error as e:
            logger.error(f"Error updating columns: {e}")

        finally:
            if conn:
                conn.close()

    def read_column(self, column_name):
        """
        reads the specified column from the table and returns the value
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT {column_name}
                FROM {SHARED_DATA_TABLE}
                WHERE id = 1
            """
            )
            value = cursor.fetchone()

            if value:
                logger.debug(f"{column_name} read from db: {value[0]}")
                return value[0]
            else:
                logger.warn(f"No {column_name} data found.")
                return None

        except sqlite3.Error as e:
            logger.error(f"Error reading {column_name} value:", e)
            return None

        finally:
            if conn:
                conn.close()

    def read_multiple_columns(self, column_names: tuple):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            select_query = "SELECT {} FROM {}".format(
                ", ".join(column_names), SHARED_DATA_TABLE
            )
            cursor.execute(select_query)
            result: tuple = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error reading {column_names}:", e)
            return None

        finally:
            if conn:
                conn.close()

        return result


if __name__ == "__main__":
    # test write_column and read_column
    db_interface = DbInterface()
    written_temeprature = 0.9
    db_interface.update_column(
        SharedDataColumns.LAST_TEMPERATURE.value, written_temeprature
    )
    temperature_value = db_interface.read_column(
        SharedDataColumns.LAST_TEMPERATURE.value
    )
    assert (
        written_temeprature == temperature_value
    ), "Temperature values don't match in the datbase"

    ## test update_multiple_columns
    column_names: tuple = (
        SharedDataColumns.LAST_TEMPERATURE.value,
        SharedDataColumns.LAST_TURNED_ON.value,
    )
    values: tuple = (21.4, "test_val")
    db_interface.update_multiple_columns(column_names, values)

    ## test read_multiple_columns
    result = db_interface.read_multiple_columns(
        (
            SharedDataColumns.LAST_TEMPERATURE.value,
            SharedDataColumns.LAST_TURNED_ON.value,
        )
    )
    assert result == values, "read_multiple_columns failed to read the right values"
    print("DbInterface class: all unit tests passed")
