import datetime
from threading import Thread
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session, jsonify
from flask_login import login_required, current_user


from app.threadManager.threadFactory import ThreadFactory
from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.DatabaseAccess.DbTables import SharedDataColumns
from app.api.Config import DeviceStatus, RUNNING_MODE
from app.api.Registration.Registrar import Registrar
from app.api.Relays.RelayController import RelayController

from . import gameSetup
from .forms import (
    GameSetupForm,
    ActiveGamesForm,
    AddScoreCardForm,
    DeactivateGameForm,
    UpdateGameDetailsForm,
)

db_api: DbInterface = DbInterface()
registrar = Registrar()
print(f"gameSetup views.py ID OF REGISTRAR = {id(registrar)}")
thread_factory = ThreadFactory()


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


@gameSetup.route("/Thermostat", methods=["GET", "POST"])
def Thermostat():
    if thread_factory.is_thread_active("thermo_thread"):
        flash("Thermostat is already active")
    else:
        thermo_thread = thread_factory.get_thread_instance(
            "thermo_thread", target_temperature=22.0, db_interface=db_api
        )
        thermo_thread.start()
        flash("Thermostat thread started")
    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/ThermostatOff", methods=["GET", "POST"])
def ThermostatOff():
    print("trying to turn off")
    if thread_factory.kill_thread("thermo_thread"):
        flash("Thermostat thread terminated")
        thread_factory.thread_map["thermo_thread"]["instance"] = None
    else:
        flash("failed to terminate thread")
    return render_template("gameSetup/gameSetupHomePage.html")
