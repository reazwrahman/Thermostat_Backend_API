from threading import Thread 
from application import app_wrapper 
from app.gameSetup.views import thread2

main_thread = Thread(target = app_wrapper, name='flask_app')  
thermo_thread = Thread(target = thread2, name='thermostat') 