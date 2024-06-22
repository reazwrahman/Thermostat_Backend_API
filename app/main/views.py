from flask import (
    render_template,
    redirect,
    url_for,
    abort,
    flash,
    request,
    current_app,
    make_response,
    Response, 
    jsonify
)
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from datetime import datetime

from api.DatabaseAccess.DbInterface import DbInterface
from api.DatabaseAccess.DbTables import SharedDataColumns
from api.Utility import Utility 
from api.UtilLogHelper import UtilLogHelper 
from api.Config import RUNNING_MODE

utility = Utility()
db_api: DbInterface = DbInterface()


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["FLASKY_SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(
                "Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n"
                % (query.statement, query.parameters, query.duration, query.context)
            )
    return response


@main.route("/shutdown")
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        abort(500)
    shutdown()
    return "Shutting down..."


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", isAdmin=True)


@main.route("/health", methods=["GET"])
def health():  
    timestamp = utility.get_est_time_now()
    response = jsonify(message="OK", timestamp=timestamp)
    response.status_code = 200
    return response 

@main.route("/currentState", methods=["GET"])
def state(): 
    current_state = utility.get_latest_state() 
    current_state["on_for_minutes"] = utility.get_time_delta_from_hour_minutes(current_state[SharedDataColumns.LAST_TURNED_ON.value]) 
    current_state["off_for_minutes"] = utility.get_time_delta_from_hour_minutes(current_state[SharedDataColumns.LAST_TURNED_OFF.value])
    return jsonify(current_state), 200


@main.route("/stateHistory", methods=["GET"])
def stateHistory():
    return UtilLogHelper.get_state_records_jsonified() 


@main.route("/errorLogs", methods=["GET"])
def errorLogs():
    logs = UtilLogHelper.get_error_logs() 
    return Response(logs, mimetype='application/json') 

@main.route("/deviceConfigs", methods=["GET"]) 
def deviceConfigs(): 
    configs = {}  
    configs["maximum_on_time"] = db_api.read_column(SharedDataColumns.MAXIMUM_ON_TIME.value)
    configs["minimum_on_time"] = db_api.read_column(SharedDataColumns.MINIMUM_ON_TIME.value) 
    configs["cool_down_period"] = db_api.read_column(SharedDataColumns.COOLDOWN_PERIOD.value) 
    configs["running_mode"] = RUNNING_MODE.value 
    return jsonify(configs), 200 

@main.route("/deviceConfigs", methods=["POST"]) 
def postDeviceConfigs():  
    request_body = request.get_json()  
    update_columns = [] 
    update_values = [] 
    columns = [SharedDataColumns.MINIMUM_ON_TIME.value, SharedDataColumns.MAXIMUM_ON_TIME.value, SharedDataColumns.COOLDOWN_PERIOD.value]
    for each in request_body: 
        if each in columns:  
            update_columns.append(each)
            update_values.append(request_body[each])
    
    db_api.update_multiple_columns(tuple(update_columns), tuple(update_values))

    configs = {}  
    configs["message"] = "update successful" 
    configs["maximum_on_time"] = db_api.read_column(SharedDataColumns.MAXIMUM_ON_TIME.value)
    configs["minimum_on_time"] = db_api.read_column(SharedDataColumns.MINIMUM_ON_TIME.value) 
    configs["cool_down_period"] = db_api.read_column(SharedDataColumns.COOLDOWN_PERIOD.value) 
    configs["running_mode"] = RUNNING_MODE.value 
    return jsonify(configs), 200

