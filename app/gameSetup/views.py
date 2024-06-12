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
from app.api.Config import DeviceTypes,COOL_DOWN_PERIOD, MINIMUM_ON_TIME, SWITCH_KEY, THERMO_THREAD, AC_THREAD, ThermoStatActions

from . import gameSetup 



utility = Utility()
db_api: DbInterface = DbInterface()
registrar = Registrar()
thread_factory = ThreadFactory()

logger = logging.getLogger(__name__)

@gameSetup.route("/", methods=["GET", "POST"])
def displayNavigations():
    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/TurnOn", methods=["GET"])
def TurnOn():
    relay_controller: RelayController = registrar.get_relay_controllers(
        RUNNING_MODE.value
    )
    device_is_on: bool = (
        db_api.read_column(SharedDataColumns.DEVICE_STATUS.value)
        == DeviceStatus.ON.value
    )

    if device_is_on:
        flash("Device is already ON, nothing to do")
    else:
        if relay_controller.turn_on():
            flash("Device Turned ON")
        else:
            flash("failed to turn device on")
    return render_template("gameSetup/gameSetupHomePage.html") 

@gameSetup.route("/on", methods=["GET", "POST"])
def on(): 
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)  

    try: 
        status:States = gate_keeper.turn_on()  
        if status == States.ALREADY_ON:  
            response = jsonify(status=States.ALREADY_ON.value, timestamp=utility.get_est_time_now())
            response.status_code = 201 
            return response  
        
        elif status == States.TURNED_ON: 
            response = jsonify(status=States.TURNED_ON.value, timestamp=utility.get_est_time_now())
            response.status_code = 200 
            return response 

        elif status == States.REQUEST_DENIED:  
            time_elapsed = utility.get_time_delta(db_api.read_column(SharedDataColumns.LAST_TURNED_OFF.value))  
            time_remaining = round(COOL_DOWN_PERIOD - time_elapsed, 2)
            payload = dict()
            payload["status"] = States.REQUEST_DENIED.value 
            payload["cool_down_period"] = f"{COOL_DOWN_PERIOD} minutes"
            #payload["time_elapsed"] = f"{round(time_elapsed, 2)} minutes" #ommitted for now, to reduce payload size
            #payload["time_remaining"] = f"{round(time_remaining, 2)} minutes"
            payload["message"] = f"Device needs to be in cool down for another {time_remaining} minutes" 
            #payload["timestamp"] = utility.get_est_time_now()
            response = jsonify(payload)
            response.status_code = 403 
            return response         
        else: 
            response = jsonify(message="unexpected response from gatekeeper", timestamp=utility.get_est_time_now())
            response.status_code = 500 
            return response    
    except: 
        response = jsonify(message=States.NO_ACTION.value, timestamp=utility.get_est_time_now())
        response.status_code = 500 
        return response  


@gameSetup.route("/forcedOn", methods=["POST"])
def forcedOn():  

    request_body = request.get_json()
    if not request_body or 'switch_key' not in request_body:
        return jsonify({'error': 'Missing switch key'}), 401  # Unauthorized if the key is missing
    
    switch_key = request_body['switch_key'] 

    if switch_key != SWITCH_KEY:  
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(status="Unauthorized to perform switch", timestamp=utility.get_est_time_now())
        response.status_code = 401 
        return response

    gate_keeper = PowerControlGateKeeper(db_interface=db_api)  

    try: 
        status:States = gate_keeper.forced_turn_on()  
        if status == States.ALREADY_ON:  
            response = jsonify(status=States.ALREADY_ON.value, timestamp=utility.get_est_time_now())
            response.status_code = 201 
            return response  
        
        elif status == States.TURNED_ON: 
            response = jsonify(status=States.TURNED_ON.value, timestamp=utility.get_est_time_now())
            response.status_code = 200 
            return response 
  
        else: 
            response = jsonify(message="unexpected response from gatekeeper", timestamp=utility.get_est_time_now())
            response.status_code = 500 
            return response    
    except: 
        response = jsonify(message=States.NO_ACTION.value, timestamp=utility.get_est_time_now())
        response.status_code = 500 
        return response 
        


@gameSetup.route("/TurnOff", methods=["GET", "POST"])
def TurnOff():
    relay_controller: RelayController = registrar.get_relay_controllers(
        RUNNING_MODE.value
    )
    device_is_on: bool = (
        db_api.read_column(SharedDataColumns.DEVICE_STATUS.value)
        == DeviceStatus.ON.value
    )

    if not device_is_on:
        flash("Device is already OFF, nothing to do")
    else:
        if relay_controller.turn_off():
            flash("Device Turned OFF")
        else:
            flash("failed to turn device off")
    return render_template("gameSetup/gameSetupHomePage.html") 


@gameSetup.route("/off", methods=["GET", "POST"])
def off(): 
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)  

    try: 
        status:States = gate_keeper.turn_off()  
        if status == States.ALREADY_OFF:  
            response = jsonify(status=States.ALREADY_OFF.value, timestamp=utility.get_est_time_now())
            response.status_code = 201 
            return response  
        
        elif status == States.TURNED_OFF: 
            response = jsonify(status=States.TURNED_OFF.value, timestamp=utility.get_est_time_now())
            response.status_code = 200 
            return response 

        elif status == States.REQUEST_DENIED:  
            time_elapsed = utility.get_time_delta(db_api.read_column(SharedDataColumns.LAST_TURNED_ON.value))  
            time_remaining = round(MINIMUM_ON_TIME - time_elapsed, 2)
            payload = dict()
            payload["status"] = States.REQUEST_DENIED.value 
            payload["minimum_on_time"] = f"{MINIMUM_ON_TIME} minutes"
            #payload["time_elapsed"] = f"{round(time_elapsed, 2)} minutes"
            #payload["time_remaining"] = f"{round(time_remaining, 2)} minutes"
            payload["message"] = f"Device needs to be on for at least another {time_remaining} minutes" 
            #payload["timestamp"] = utility.get_est_time_now()
            response = jsonify(payload)
            response.status_code = 403 
            return response         
        else: 
            response = jsonify(message="unexpected response from gatekeeper", timestamp=utility.get_est_time_now())
            response.status_code = 500 
            return response  
    except: 
        response = jsonify(message=States.NO_ACTION.value, timestamp=utility.get_est_time_now())
        response.status_code = 500 
        return response


@gameSetup.route("/forcedOff", methods=["POST"])
def forcedOff():   
    
    request_body = request.get_json()
    if not request_body or 'switch_key' not in request_body:
        return jsonify({'error': 'Missing switch key'}), 401  # Unauthorized if the key is missing
    
    switch_key = request_body['switch_key'] 

    if switch_key != SWITCH_KEY:  
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(status="Unauthorized to perform switch", timestamp=utility.get_est_time_now())
        response.status_code = 401 
        return response 
    
    gate_keeper = PowerControlGateKeeper(db_interface=db_api)
    try: 
        status:States = gate_keeper.forced_turn_off()  
        if status == States.ALREADY_OFF:  
            response = jsonify(status=States.ALREADY_OFF.value, timestamp=utility.get_est_time_now())
            response.status_code = 204 
            return response  
        
        elif status == States.TURNED_OFF: 
            response = jsonify(status=States.TURNED_OFF.value, timestamp=utility.get_est_time_now())
            response.status_code = 200 
            return response      
        else: 
            response = jsonify(message="unexpected response from gatekeeper", timestamp=utility.get_est_time_now())
            response.status_code = 500 
            return response  
    except: 
        response = jsonify(message=States.NO_ACTION.value, timestamp=utility.get_est_time_now())
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
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') 
    if humidity:
        response = jsonify(message="available", timestamp=timestamp, humidity= humidity)  
        response.status_code = 200
    else: 
        response = jsonify(message="n/a", timestamp=timestamp, humidity= "NULL")   
        response.status_code = 500
    return response


''' 
expected request body={ 
"switch_key"=key,  
"device" = check devicetypes enum values,
"action" = ON/OFF/UPDATE, 
"target_temperature" = float value (only needed for on action)
}
'''
@gameSetup.route("/ThermoStat", methods=["POST"])  
def ThermoStat():  
    ## validate key/signature
    request_body = request.get_json() 

    validation_result = __validate_thermo_request_body(request_body)
    if validation_result: 
        return validation_result

    if request_body["action"] == ThermoStatActions.ON.value: 
        return __thermostat_on_action(request_body["device"], request_body["target_temperature"])


def __thermostat_on_action(device_name, target_temperature): 
    ## get current status of the themostat threads
    thread_status:dict = __get_thread_active_status()

    if thread_status[THERMO_THREAD]:  
        return jsonify({'error': 'Thermostat is actively running with the Heater'}), 409 
            
    elif thread_status[AC_THREAD]: 
        return jsonify({'error': 'Thermostat is actively running with the AC'}), 409 
    
    else: 
        if device_name == DeviceTypes.AC.value:
            ac_thread = thread_factory.get_thread_instance(
                AC_THREAD, target_temperature=target_temperature, db_interface=db_api
            )
            ac_thread.start()
            return jsonify({'message': 'Thermostat turned on with AC'}), 200
    
        else: 
            heater_thread = thread_factory.get_thread_instance(
                THERMO_THREAD, target_temperature=target_temperature, db_interface=db_api
            )
            heater_thread.start()
            return jsonify({'message': 'Thermostat turned on with Heater'}), 200



def __validate_thermo_request_body(request_body):  
    if not request_body or 'switch_key' not in request_body:
        return jsonify({'error': 'Missing switch key'}), 401  # Unauthorized if the key is missing
    
    switch_key = request_body['switch_key'] 

    if switch_key != SWITCH_KEY:  
        logger.error(f"expected key {SWITCH_KEY}, actual key {switch_key}")
        response = jsonify(status="Unauthorized to perform switch", timestamp=utility.get_est_time_now())
        response.status_code = 401 
        return response  
    
    ## validate request body 
    if "action" not in request_body:
        return jsonify({'error': 'Missing action'}), 400  # bad request 

    if "device" not in request_body: 
        return jsonify({'error': 'Missing device'}), 400  # bad request  

    if request_body["action"] == ThermoStatActions.ON.value: 
        if "target_temperature" not in request_body: 
            return jsonify({'error': 'Missing target temperature'}), 400  # bad request 
    
    return None



@gameSetup.route("/ThermostatOn", methods=["GET", "POST"])
def Thermostat(): 
    thread_status:dict = __get_thread_active_status()
    if thread_status[THERMO_THREAD]:  
        # TODO: create http response 
        return "thermo thread active, can't do nothing" 
    
    elif thread_status[AC_THREAD]: 
        # TODO: create http response 
        return "ac thread active, can't do nothing" 
    else:
        thermo_thread = thread_factory.get_thread_instance(
            THERMO_THREAD, target_temperature=22.0, db_interface=db_api
        )
        thermo_thread.start()
        return "thermo thread started" 
    


@gameSetup.route("/ThermostatOff", methods=["GET", "POST"])
def ThermostatOff(): 
    thread_status:dict = __get_thread_active_status() 
    if not thread_status[THERMO_THREAD]: 
        # TODO: create http 204 
        return "already off nothing to do"

    logger.info("Main Thread::ThermostatOff trying to turn off")
    if thread_factory.kill_thread(THERMO_THREAD):
        thread_factory.thread_map[THERMO_THREAD]["instance"] = None 
        # TODO: create http response 200"
        return "thread killed"
    else:
        # TODO: create http response 400"
        return "failed to kill"


@gameSetup.route("/ACThreadOn", methods=["GET", "POST"])
def ACThreadOn():
    thread_status:dict = __get_thread_active_status() 
    if thread_status[THERMO_THREAD]:  
        # TODO: create http response 
        return "thermo thread active, can't do nothing" 
    
    elif thread_status[AC_THREAD]: 
        # TODO: create http response 
        return "ac thread active, can't do nothing" 

    else:
        ac_thread = thread_factory.get_thread_instance(
            AC_THREAD, target_temperature=22.0, target_humidity=55.0, db_interface=db_api
        )
        ac_thread.start()
        return "AC thread started"
    


@gameSetup.route("/ACThreadOff", methods=["GET", "POST"])
def ACThreadOff():
    thread_status:dict = __get_thread_active_status() 
    if not thread_status[AC_THREAD]: 
        # TODO: create http 204 
        return "already off nothing to do"

    logger.info("Main Thread::ThermostatOff trying to turn off")
    if thread_factory.kill_thread(AC_THREAD):
        thread_factory.thread_map[AC_THREAD]["instance"] = None 
        # TODO: create http response 200"
        return "thread killed"
    else:
        # TODO: create http response 400"
        return "failed to kill"

@gameSetup.route("/threadStatus", methods=["GET", "POST"])
def threadStatus(): 
    thread_status:dict = __get_thread_active_status()  
    return str(thread_status)



def __get_thread_active_status(): 
    status = dict() 
    status[AC_THREAD] = False 
    status[THERMO_THREAD] = False 
    
    if thread_factory.is_thread_active(AC_THREAD): 
        status[AC_THREAD] = True 
    
    if thread_factory.is_thread_active(THERMO_THREAD): 
        status[THERMO_THREAD] = True  
    
    return status