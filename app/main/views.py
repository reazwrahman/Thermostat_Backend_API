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

from api.Utility import Utility 
from api.UtilLogHelper import UtilLogHelper 
from api.Config import MAXIMUM_ON_TIME, COOL_DOWN_PERIOD, MINIMUM_ON_TIME, RUNNING_MODE

utility = Utility()


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
    return jsonify(utility.get_latest_state())


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
    configs["maximum_on_time"] = MAXIMUM_ON_TIME 
    configs["minimum_on_time"] = MINIMUM_ON_TIME 
    configs["cool_down_period"] = COOL_DOWN_PERIOD 
    configs["running_mode"] = RUNNING_MODE.value 
    return jsonify(configs), 200

