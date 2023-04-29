from threading import Thread 

global thermo_thread_started
thermo_thread_started = False 

def thread2(): 
    import time 
    i = 0  
    while True:
        print(f"hello world im running concurrently {i}") 
        i+=1 
        time.sleep(2)

thermo_thread = Thread(target = thread2, name='thermostat') 