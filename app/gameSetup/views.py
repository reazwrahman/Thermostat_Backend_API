import serial 
from threading import Thread 
from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from thread_manager import thermo_thread, thermo_thread_started
from . import gameSetup
from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm

# Open the serial port at the specified baudrate
#ser = serial.Serial('/dev/cu.usbmodem14101', 9600)
#ser = serial.Serial('/dev/ttyACM0',9600)

@gameSetup.route('/', methods=['GET', 'POST']) 
def displayNavigations(): 
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/TurnOn', methods=['GET'])  
def TurnOn():  
    try:
        data = 'G'
        ser.write(data.encode())
        flash('led turned on')  
    except Exception as e: 
         flash('failed to turn led on') 
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')
           


@gameSetup.route('/TurnOff', methods=['GET', 'POST']) 
def TurnOff(): 
    try:
        data = 'P'
        ser.write(data.encode())
        flash('led turned off')  
    except Exception as e: 
         flash('failed to turn led off')  
         print(e)
    return render_template ('gameSetup/gameSetupHomePage.html')  

@gameSetup.route('/thread2', methods=['GET', 'POST']) 
def thread2():   
    global thermo_thread_started
    if not thermo_thread_started: 
        thermo_thread.start() 
        thermo_thread_started = True
    return "running a new thread"


