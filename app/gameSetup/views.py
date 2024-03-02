import datetime
from threading import Thread
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user

from app.threadManager.threadFactory import ThreadFactory
from . import gameSetup

from app.api.DatabaseAccess.DbInterface import DbInterface
from app.api.DatabaseAccess.DbTables import SharedDataColumns
from app.api.Config import DeviceStatus, RUNNING_MODE
from app.api.Registration.Registrar import Registrar, RunningModes
from app.api.Relays.RelayController import RelayController

from app.api.pinController import PinController
from app.api.thermoStat import ThermoStat

from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import (
    GameSetupForm,
    ActiveGamesForm,
    AddScoreCardForm,
    DeactivateGameForm,
    UpdateGameDetailsForm,
)

## initialize api instance(s)
pin_controller = PinController()
db_api: DbInterface = DbInterface()


@gameSetup.route("/", methods=["GET", "POST"])
def displayNavigations():
    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/TurnOn", methods=["GET"])
def TurnOn():
    relay_controller: RelayController = Registrar.get_relay_controllers(RUNNING_MODE)
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
    relay_controller: RelayController = Registrar.get_relay_controllers(RUNNING_MODE)
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


@gameSetup.route("/TurnOnPowerCycle", methods=["GET", "POST"])
def TurnOnPowerCycle():
    ## place_holder code
    power_cycle = ThreadFactory.get_thread_instance(
        "power_cycle", power_on_minutes=1, power_off_minutes=1
    )
    if power_cycle is not None:
        power_cycle.start()
        flash("power cycle thread started for the first time")
    else:
        flash(
            "a power cycle is already in progress. Kill it first and then request a new one"
        )

    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/TurnOffPowerCycle", methods=["GET", "POST"])
def TurnOffPowerCycle():
    killed = ThreadFactory.kill_thread("power_cycle")
    flash("Power Cycle is terminated")
    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/TurnOnTempControl", methods=["GET", "POST"])
def TurnOnTempControl():
    ## place_holder code
    heater_control = ThreadFactory.get_thread_instance("heater_control", target_temp=25)
    if heater_control is not None:
        heater_control.start()
        flash("heater_control thread started for the first time")
    else:
        flash(
            "a heater_control thread is already in progress. Kill it first and then request a new one"
        )

    return render_template("gameSetup/gameSetupHomePage.html")


@gameSetup.route("/TurnOffTempControl", methods=["GET", "POST"])
def TurnOffTempControl():
    killed = ThreadFactory.kill_thread("heater_control")
    flash("heater_control thread is terminated")
    return render_template("gameSetup/gameSetupHomePage.html")
