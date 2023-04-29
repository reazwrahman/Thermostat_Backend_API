from threading import Thread 
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from thread_manager import thermo_thread, thermo_thread_started
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
        GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW) 
        GPIO.output(led_pin, GPIO.HIGH)
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
        GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW) 
        GPIO.output(led_pin, GPIO.LOW)
    except Exception as e: 
         flash('failed to turn led on') 
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')  

@gameSetup.route('/thread2', methods=['GET', 'POST']) 
def thread2():   
    global thermo_thread_started
    if not thermo_thread_started: 
        thermo_thread.start() 
        thermo_thread_started = True
    return "running a new thread"


