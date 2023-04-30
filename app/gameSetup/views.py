import datetime
from threading import Thread 
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from thread_manager import thermo_thread
from . import gameSetup
from device_history import DeviceHistory 
from app.api.pinController import PinController
from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm

## initialize api instance(s)
pin_controller = PinController()


@gameSetup.route('/', methods=['GET', 'POST']) 
def displayNavigations(): 
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/TurnOn', methods=['GET'])  
def TurnOn(): 
    if DeviceHistory.is_on: 
         flash ("Device is already ON, nothing to do") 
    else:
        if pin_controller.turn_on():
            flash ("Device Turned ON") 
            DeviceHistory.is_on = True
            DeviceHistory.last_turned_on = datetime.datetime.now()
    return render_template ('gameSetup/gameSetupHomePage.html')
           


@gameSetup.route('/TurnOff', methods=['GET', 'POST']) 
def TurnOff():  
    if not DeviceHistory.is_on: 
         flash ("Device is already OFF, nothing to do")  
    else:
        if pin_controller.turn_off(): 
            flash ("Device Turned OFF") 
            DeviceHistory.is_on = False
            DeviceHistory.last_turned_off = datetime.datetime.now()
    return render_template ('gameSetup/gameSetupHomePage.html')  

@gameSetup.route('/GetTemp', methods=['GET', 'POST']) 
def GetTemp():   
    if not thermo_thread.thermostat_started: 
        thermo_thread.start() 
        thermo_thread.thermostat_started = True 

    thermo_stat = thermo_thread.get_thermostat()
    temperature = thermo_stat.get_temperature()
    humidity = thermo_stat.get_humidity() 

    if temperature and humidity:
        flash(f"Temperature: {temperature} degree Celsius") 
        flash(f"Humidity: {humidity} %") 
    else: 
        flash(f" Couldn't get sensor reading. Try again in a few")  
    
    return render_template ('gameSetup/gameSetupHomePage.html') 



