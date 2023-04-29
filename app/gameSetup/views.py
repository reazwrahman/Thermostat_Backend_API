from threading import Thread 
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from thread_manager import thermo_thread_helper, thermo_thread
from . import gameSetup
from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm

try:
    import RPi.GPIO as GPIO 
except: 
    print (f'couldnt import RPi, if not on a laptop something is wrong')


@gameSetup.route('/', methods=['GET', 'POST']) 
def displayNavigations(): 
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/TurnOn', methods=['GET'])  
def TurnOn(): 
    led_pin = 26  
    try:
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(led_pin, GPIO.OUT) 
        GPIO.output(led_pin, GPIO.HIGH)  
        flash('LED turned ON') 
    except Exception as e: 
         flash('failed to turn led on') 
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')
           


@gameSetup.route('/TurnOff', methods=['GET', 'POST']) 
def TurnOff(): 
    led_pin = 26  
    try:
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(led_pin, GPIO.OUT)
        GPIO.output(led_pin, GPIO.LOW) 
        flash('LED turned OFF')
    except Exception as e: 
         flash('failed to turn led on') 
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')  

@gameSetup.route('/GetTemp', methods=['GET', 'POST']) 
def GetTemp():   
    if not thermo_thread_helper.thermostat_started: 
        thermo_thread.start() 
        thermo_thread_helper.thermostat_started = True 

    thermo_stat = thermo_thread_helper.get_thermostat()
    temperature = thermo_stat.get_temperature()
    humidity = thermo_stat.get_humidity() 

    if temperature and humidity:
        flash(f" Current Temperature: {temperature} degree Celsius") 
        flash(f" Current Humidity: {humidity} %") 
    else: 
        flash(f" Couldn't get sensor reading. Try again in a few")  
    
    return render_template ('gameSetup/gameSetupHomePage.html') 



