import datetime
from threading import Thread
import logging
from flask import render_template, redirect, request, url_for, flash, session, jsonify
from flask_login import login_required, current_user


from app.threadManager.threadFactory import ThreadFactory
from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.DatabaseAccess.DbTables import SharedDataColumns
from app.api.Config import DeviceStatus, RUNNING_MODE
from app.api.Registration.Registrar import Registrar
from app.api.Relays.PowerControlGateKeeper import PowerControlGateKeeper, States
from app.api.Relays.RelayController import RelayController
from app.api.Utility import Utility
from app.api.Config import (
    DeviceTypes,
    SWITCH_KEY,
    THERMO_THREAD,
    AC_THREAD,
    ThermoStatActions,
)

from . import gameSetup


utility = Utility()
db_api: DbInterface = DbInterface()
registrar = Registrar()
thread_factory = ThreadFactory()

logger = logging.getLogger(__name__)


@gameSetup.route("/", methods=["GET", "POST"])
def displayNavigations():
    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/on", methods=["GET", "POST"])
def on():
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)

    try:
        status: States = gate_keeper.turn_on()
        if status == States.ALREADY_ON:
            response = jsonify(
                status=States.ALREADY_ON.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 201
            return response

        elif status == States.TURNED_ON:
            response = jsonify(
                status=States.TURNED_ON.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 200
            return response

        elif status == States.REQUEST_DENIED:
            time_elapsed = utility.get_time_delta(
                db_api.read_column(SharedDataColumns.LAST_TURNED_OFF.value)
            )
            cool_down_period = db_api.read_column(
                SharedDataColumns.COOLDOWN_PERIOD.value
            )
            time_remaining = round(cool_down_period - time_elapsed, 2)
            payload = dict()
            payload["status"] = States.REQUEST_DENIED.value
            payload["cool_down_period"] = f"{cool_down_period} minutes"
            # payload["time_elapsed"] = f"{round(time_elapsed, 2)} minutes" #ommitted for now, to reduce payload size
            # payload["time_remaining"] = f"{round(time_remaining, 2)} minutes"
            payload[
                "message"
            ] = f"Device needs to be in cool down for another {time_remaining} minutes"
            # payload["timestamp"] = utility.get_est_time_now()
            response = jsonify(payload)
            response.status_code = 403
            return response
        else:
            response = jsonify(
                message="unexpected response from gatekeeper",
                timestamp=utility.get_est_time_now(),
            )
            response.status_code = 500
            return response
    except:
        response = jsonify(
            message=States.NO_ACTION.value, timestamp=utility.get_est_time_now()
        )
        response.status_code = 500
        return response


@gameSetup.route("/forcedOn", methods=["POST"])
def forcedOn():
    request_body = request.get_json()
    if not request_body or "switch_key" not in request_body:
        return (
            jsonify({"error": "Missing switch key"}),
            401,
        )  # Unauthorized if the key is missing

    switch_key = request_body["switch_key"]

    if switch_key != SWITCH_KEY:
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(
            status="Unauthorized to perform switch",
            timestamp=utility.get_est_time_now(),
        )
        response.status_code = 401
        return response

    gate_keeper = PowerControlGateKeeper(db_interface=db_api)

    try:
        status: States = gate_keeper.forced_turn_on()
        if status == States.ALREADY_ON:
            response = jsonify(
                status=States.ALREADY_ON.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 201
            return response

        elif status == States.TURNED_ON:
            response = jsonify(
                status=States.TURNED_ON.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 200
            return response

        else:
            response = jsonify(
                message="unexpected response from gatekeeper",
                timestamp=utility.get_est_time_now(),
            )
            response.status_code = 500
            return response
    except:
        response = jsonify(
            message=States.NO_ACTION.value, timestamp=utility.get_est_time_now()
        )
        response.status_code = 500
        return response


@gameSetup.route("/off", methods=["GET", "POST"])
def off():
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)

    try:
        status: States = gate_keeper.turn_off()
        if status == States.ALREADY_OFF:
            response = jsonify(
                status=States.ALREADY_OFF.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 201
            return response

        elif status == States.TURNED_OFF:
            response = jsonify(
                status=States.TURNED_OFF.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 200
            return response

        elif status == States.REQUEST_DENIED:
            time_elapsed = utility.get_time_delta(
                db_api.read_column(SharedDataColumns.LAST_TURNED_ON.value)
            )
            minimum_on_time: int = db_api.read_column(
                SharedDataColumns.MINIMUM_ON_TIME.value
            )
            time_remaining = round(minimum_on_time - time_elapsed, 2)
            payload = dict()
            payload["status"] = States.REQUEST_DENIED.value
            payload["minimum_on_time"] = f"{minimum_on_time} minutes"
            # payload["time_elapsed"] = f"{round(time_elapsed, 2)} minutes"
            # payload["time_remaining"] = f"{round(time_remaining, 2)} minutes"
            payload[
                "message"
            ] = f"Device needs to be on for at least another {time_remaining} minutes"
            # payload["timestamp"] = utility.get_est_time_now()
            response = jsonify(payload)
            response.status_code = 403
            return response
        else:
            response = jsonify(
                message="unexpected response from gatekeeper",
                timestamp=utility.get_est_time_now(),
            )
            response.status_code = 500
            return response
    except:
        response = jsonify(
            message=States.NO_ACTION.value, timestamp=utility.get_est_time_now()
        )
        response.status_code = 500
        return response


@gameSetup.route("/forcedOff", methods=["POST"])
def forcedOff():
    request_body = request.get_json()
    if not request_body or "switch_key" not in request_body:
        return (
            jsonify({"error": "Missing switch key"}),
            401,
        )  # Unauthorized if the key is missing

    switch_key = request_body["switch_key"]

    if switch_key != SWITCH_KEY:
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(
            status="Unauthorized to perform switch",
            timestamp=utility.get_est_time_now(),
        )
        response.status_code = 401
        return response

    gate_keeper = PowerControlGateKeeper(db_interface=db_api)
    try:
        status: States = gate_keeper.forced_turn_off()
        if status == States.ALREADY_OFF:
            response = jsonify(
                status=States.ALREADY_OFF.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 204
            return response

        elif status == States.TURNED_OFF:
            response = jsonify(
                status=States.TURNED_OFF.value, timestamp=utility.get_est_time_now()
            )
            response.status_code = 200
            return response
        else:
            response = jsonify(
                message="unexpected response from gatekeeper",
                timestamp=utility.get_est_time_now(),
            )
            response.status_code = 500
            return response
    except:
        response = jsonify(
            message=States.NO_ACTION.value, timestamp=utility.get_est_time_now()
        )
        response.status_code = 500
        return response


@gameSetup.route("/GetTemp", methods=["GET", "POST"])
def GetTemp():
    temperature = db_api.read_column(SharedDataColumns.LAST_TEMPERATURE.value)

    if temperature:
        flash(f"Temperature: {temperature} degree Celsius")
    else:
        flash(f" Couldn't get sensor reading. Try again in a few")

    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/GetHumidity", methods=["GET"])
def GetHumidity():
    humidity = db_api.read_column(SharedDataColumns.LAST_HUMIDITY.value)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if humidity:
        response = jsonify(message="available", timestamp=timestamp, humidity=humidity)
        response.status_code = 200
    else:
        response = jsonify(message="n/a", timestamp=timestamp, humidity="NULL")
        response.status_code = 500
    return response


""" 
expected request body={ 
"switch_key"=key,  
"device" = check devicetypes enum values,
"action" = ON/OFF/UPDATE, 
"target_temperature" = float value (only needed for on action)
}
"""


@gameSetup.route("/thermostat", methods=["PUT"])
def updateThermostat():
    request_body = request.get_json()
    __validate_thermo_request_body(request_body)

    thread_status: dict = __get_thread_active_status()

    if request_body["device"] == DeviceTypes.AC.value:
        if not thread_factory.is_thread_active(AC_THREAD):
            return jsonify({"error": "Bad Request, Thermostat is not on for AC"}), 400

    if request_body["device"] == DeviceTypes.HEATER.value:
        if not thread_factory.is_thread_active(THERMO_THREAD):
            return (
                jsonify({"error": "Bad Request, Thermostat is not on for Heater"}),
                400,
            )

    if request_body["action"] == ThermoStatActions.UPDATE.value:
        db_api.update_column(
            SharedDataColumns.TARGET_TEMPERATURE.value,
            request_body["target_temperature"],
        )
        message = f'Target temperature is updated to {request_body["target_temperature"]} degree celsius for Thermostat running with {request_body["device"]}'
        return jsonify({"message": message}), 201

    else:
        return jsonify({"error": "Bad Request, action is not recognized"}), 400


@gameSetup.route("/thermostat", methods=["POST"])
def thermostat():
    request_body = request.get_json()

    validation_result = __validate_thermo_request_body(request_body)
    if validation_result:
        return validation_result

    if request_body["action"] == ThermoStatActions.ON.value:
        return __thermostat_on_action(
            request_body["device"], request_body["target_temperature"]
        )

    elif request_body["action"] == ThermoStatActions.OFF.value:
        return __thermostat_off_action(
            request_body["device"], request_body["target_temperature"]
        )

    else:
        logger.error(
            f'GameSetup/views::ThermoStat POST, invalid action: {request_body["action"]}'
        )


def __thermostat_off_action(device_name, target_temperature):
    ## get current status of the themostat threads
    thread_status: dict = __get_thread_active_status()

    if device_name == DeviceTypes.AC.value:
        if not thread_factory.is_thread_active(AC_THREAD):
            return jsonify({"message": "Thermostat is already off for AC"}), 201
        if thread_factory.kill_thread(AC_THREAD):
            thread_factory.thread_map[AC_THREAD]["instance"] = None
            db_api.update_column(SharedDataColumns.TARGET_TEMPERATURE.value, None)
            return jsonify({"message": "Thermostat turned off for AC"}), 200

    elif device_name == DeviceTypes.HEATER.value:
        if not thread_factory.is_thread_active(THERMO_THREAD):
            return jsonify({"message": "Thermostat is already off for Heater"}), 201
        if thread_factory.kill_thread(THERMO_THREAD):
            thread_factory.thread_map[THERMO_THREAD]["instance"] = None
            db_api.update_column(SharedDataColumns.TARGET_TEMPERATURE.value, None)
            return jsonify({"message": "Thermostat turned off for Heater"}), 200

    else:
        return jsonify({"error": "Bad Request, unknown device name"}), 400


def __thermostat_on_action(device_name, target_temperature):
    ## get current status of the themostat threads
    thread_status: dict = __get_thread_active_status()

    if thread_status[THERMO_THREAD]:
        return jsonify({"error": "Thermostat is actively running with the Heater"}), 409

    elif thread_status[AC_THREAD]:
        return jsonify({"error": "Thermostat is actively running with the AC"}), 409

    else:
        db_api.update_column(
            SharedDataColumns.TARGET_TEMPERATURE.value, target_temperature
        )
        if device_name == DeviceTypes.AC.value:
            ac_thread = thread_factory.get_thread_instance(
                AC_THREAD, target_temperature=target_temperature, db_interface=db_api
            )
            ac_thread.start()
            return jsonify({"message": "Thermostat turned on with AC"}), 200

        elif device_name == DeviceTypes.HEATER.value:
            heater_thread = thread_factory.get_thread_instance(
                THERMO_THREAD,
                target_temperature=target_temperature,
                db_interface=db_api,
            )
            heater_thread.start()
            return jsonify({"message": "Thermostat turned on with Heater"}), 200

        else:
            return jsonify({"error": "Bad Request, unknown device name"}), 400


def __validate_thermo_request_body(request_body):
    if not request_body or "switch_key" not in request_body:
        return (
            jsonify({"error": "Missing switch key"}),
            401,
        )  # Unauthorized if the key is missing

    switch_key = request_body["switch_key"]

    if switch_key != SWITCH_KEY:
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(
            status="Unauthorized to perform switch",
            timestamp=utility.get_est_time_now(),
        )
        response.status_code = 401
        return response

    ## validate request body
    if "action" not in request_body:
        return jsonify({"error": "Missing action"}), 400  # bad request

    if "device" not in request_body:
        return jsonify({"error": "Missing device"}), 400  # bad request

    if (
        request_body["action"] == ThermoStatActions.ON.value
        or request_body["action"] == ThermoStatActions.UPDATE.value
    ):
        if "target_temperature" not in request_body:
            return jsonify({"error": "Missing target temperature"}), 400  # bad request

    return None


@gameSetup.route("/thermostat", methods=["GET"])
def getThermostat():
    thread_status: dict = __get_thread_active_status()
    for each in thread_status:
        if not thread_status[each]:
            thread_status[each] = DeviceStatus.OFF.value
        else:
            thread_status[each] = DeviceStatus.ON.value
    (current_temp, target_temp) = db_api.read_multiple_columns(
        (
            SharedDataColumns.LAST_TEMPERATURE.value,
            SharedDataColumns.TARGET_TEMPERATURE.value,
        )
    )
    thread_status["current_temperature"] = current_temp
    thread_status["target_temperature"] = target_temp
    thread_status["updated_on"] = utility.get_est_time_now()
    return jsonify(thread_status), 200


def __get_thread_active_status():
    status = dict()
    status[AC_THREAD] = False
    status[THERMO_THREAD] = False

    if thread_factory.is_thread_active(AC_THREAD):
        status[AC_THREAD] = True

    if thread_factory.is_thread_active(THERMO_THREAD):
        status[THERMO_THREAD] = True

    return status


### --------------------------------- ####
""" endpoints for admin use/test only """
### --------------------------------- ####


@gameSetup.route("/masterOn", methods=["GET"])
def masterOn():
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)
    status: States = gate_keeper.forced_turn_on()
    return jsonify(status.value), 200


@gameSetup.route("/masterOff", methods=["GET"])
def masterOff():
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)
    status: States = gate_keeper.forced_turn_off()
    return jsonify(status.value), 200
