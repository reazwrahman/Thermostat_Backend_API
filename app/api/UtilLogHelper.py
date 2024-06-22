import json
import logging
from enum import Enum
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)


logger = logging.getLogger(__name__)

MAX_RECORDS_TO_STORE = 20
STATE_RECORD_JSON = "state_transition_records_json.json"
ERROR_LOG = "error.log"


class UtilLogHelper:
    @staticmethod
    def record_state_changes_in_deque(state_change_event):
        try:
            with open(STATE_RECORD_JSON, "r") as json_file:
                records = json.load(json_file)
        except FileNotFoundError:  ## first record, file doesn't exist yet
            records = []

        except Exception as e:
            logger.error(
                f"UtilLogHelper::record_state_changes_in_deque exception occured {str(e)}"
            )

        if len(records) == MAX_RECORDS_TO_STORE:
            records.pop(0)

        records.append(state_change_event)

        with open(STATE_RECORD_JSON, "w") as json_file:
            json.dump(records, json_file, indent=4)

    @staticmethod
    def get_state_records_jsonified():
        try:
            with open(STATE_RECORD_JSON, "r") as json_file:
                records = json.load(json_file)
        except FileNotFoundError:  ## first record, file doesn't exist yet
            records = []

        records.reverse()  # to preserve chronological order
        return json.dumps(records, indent=4)

    @staticmethod
    def get_error_logs():
        with open(ERROR_LOG, "r") as log_file:
            log_content = log_file.read()

        log_entries = []

        # Define a regex pattern to match log entries
        log_pattern = re.compile(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w.]+) - (\w+) - (.+)"
        )

        for line in log_content.split("\n"):
            # Match the log line with the pattern
            match = log_pattern.match(line)
            if match:
                timestamp, logger, level, message = match.groups()
                log_entries.append(
                    {
                        "timestamp": timestamp,
                        "logger": logger,
                        "level": level,
                        "message": message,
                    }
                )

        # Convert the list of dictionaries to a JSON string
        return json.dumps(log_entries, indent=4)


if __name__ == "__main__":
    ## test get state records

    if os.path.exists(os.path.join(os.getcwd(), STATE_RECORD_JSON)):
        os.remove(STATE_RECORD_JSON)

    def test_get_state_records_jsonified():
        test_payload = {"test_id": 0, "event": "on"}
        total = 30
        for i in range(total):
            test_payload["test_id"] = i
            UtilLogHelper.record_state_changes_in_deque(test_payload)

        jsonified_records = UtilLogHelper.get_state_records_jsonified()
        records = json.loads(jsonified_records)

        for i in range(len(records)):
            assert records[i]["test_id"] == total - 1 - i

    test_get_state_records_jsonified()
    print("UtilLogHelper all unit tests passed")
