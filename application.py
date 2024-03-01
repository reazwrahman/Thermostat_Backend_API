import os 
from threading import Thread 
import sys
import click 

from app.threadManager.threadFactory import ThreadFactory 
from app import create_app 

app = create_app(os.getenv('FLASK_CONFIG') or 'default')




def app_wrapper(): 
    app.run (host='0.0.0.0', port=80, use_reloader=False)

if __name__ == "__main__":
    #thermo_thread = ThreadFactory.get_thread_instance("thermostat") 
    #thermo_thread.start()  
    main_thread = Thread(target = app_wrapper, name='flask_app') 
    main_thread.start()