import datetime
from threading import Thread 
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from thread_manager import ThreadFactory
from . import gameSetup
from app.api.device_history import DeviceHistory 
from app.api.pinController import PinController 
from app.api.thermoStat import ThermoStat

from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm

## initialize api instance(s)
pin_controller = PinController()  
thermo_stat = ThermoStat()



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
    temperature = thermo_stat.get_temperature()
    humidity = thermo_stat.get_humidity()  

    if temperature and humidity:
        flash(f"Temperature: {temperature} degree Celsius") 
        flash(f"Humidity: {humidity} %") 
    else: 
        flash(f" Couldn't get sensor reading. Try again in a few")  
    
    return render_template ('gameSetup/gameSetupHomePage.html')  

@gameSetup.route('/TurnOnPowerCycle', methods=['GET', 'POST']) 
def TurnOnPowerCycle():     
    ## place_holder code   
    power_cycle = ThreadFactory.get_power_cycle_thread(1,1) 
    if power_cycle is not None: 
        power_cycle.start()
        flash('power cycle thread started for the first time') 
    else: 
        flash('a power cycle is already in progress. Kill it first and then request a new one')
    
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/TurnOffPowerCycle', methods=['GET', 'POST']) 
def TurnOffPowerCycle():       
    killed = ThreadFactory.kill_power_cycle_thread()
    flash('Power Cycle is terminated') 
    
    
    return render_template ('gameSetup/gameSetupHomePage.html')
