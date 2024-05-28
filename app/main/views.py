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
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import Permission, Role, User
from ..decorators import admin_required, permission_required
from datetime import datetime

from api.Utility import Utility

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
    isAdmin = False

    if current_user.is_authenticated:
        user_object = User.query.filter_by(id=current_user.id).first()
        isAdmin = user_object.is_administrator()

    return render_template("index.html", isAdmin=True)


@main.route("/health", methods=["GET"])
def health():  
    timestamp = utility.get_est_time_now()
    response = jsonify(message="OK", timestamp=timestamp)
    response.status_code = 200
    return response 

@main.route("/state", methods=["GET"])
def state():
    return jsonify(utility.get_latest_state())

