# Project Overview

Project context can be found at this link (published version of this site), avoiding rewriting it here to maintain a single source of truth:
https://reazwrahman.github.io/thermostat_frontend/background_pages/context_page/index.html

Youtube Link to the presentation: https://www.youtube.com/watch?v=SZcvlecOQ6Y

Hardware Setup for some perspective: https://reazwrahman.github.io/thermostat_frontend/background_pages/hardware_page/index.html

The backend API uses raspberry pi as a primary microcontroller to operate a thermostat, control a 120V power relays which is connected to an electric heater and an air conditioner. This project also uses concepts like multithreading and factory pattern to create reusable and maintainable software. 

Attention: python version to use: 3.9

## First Time Setup Instructions  

- Make sure to install Python 3.9 (Any other version of Python will NOT be  
compatible with this project). 

- for mac: ```brew install python@3.9```, verify with: ```python3.9 --version```

- create a project directory and create a Python virtual environment with: 
```python3.9 -m venv venv``` 

- activate the virtual environment: ```source venv/bin/activate``` 

- clone this repository: ```git clone https://github.com/reazwrahman/Thermostat_Backend_API.git```  

- go to root directory: ```cd Thermostat_Backend_API```

- install the dependencies: ```pip install -r requirements.txt``` 

- open this file: app/api/Config.py and make sure RUNNING_MODE is set to SIM (simulation), look for this line: ```RUNNING_MODE = RunningModes.SIM``` 

- and that's it! You are ready to go, run: ```python3 application.py``` 

- take a note of your computer's ip address, the api will be available at: 
```<your-ip>:8080```, you can quickly check the health of the API in your browser 
by visiting: ```http://<your-ip>:8080/health```, if you see 
```"message": "OK", ``` - everything is working great! 



## Test Instruction for Target Hardware

- Navigate one directory up (where venv will be located) and create a backup folder. 
If it's already created and backup config exists there, jump to git stash and git pull 

- make sure ```app/api/Config.py``` has the correct running mode and device config values  

- specifically, make sure the running mode is set to"TARGET". Also, make sure "MINIMUM_ON_TIME", 
"MAXIMUM_ON_TIME", "COOL_DOWN_PERIOD" have reasonable values for the target 
state.  

- Save the ```app/api/Config.py``` file inside backup with target related settings. 
You can do this by running this from the root directory of this application: 
```cp app/api/Config.py ../backup/.```

- stash local changes by running ```git stash``` 

- pull changes from the remote: ```git pull``` 

- update the config with backed up config (we have to do this because we are not  
guaranteed which configuration the remote main has, it could have sim configs): 
```cp ../backup/Config.py app/api/Config.py``` 

- activate venv and you are ready to test! : ```python3 application.py```


### TMUX instructions for Target Machine 
- to list all tmux sessions: ```tmux ls``` 
- to attach to a session: ```tmux attach-session -t <id>``` 
- to kill a session: ```tmux kill-session -t <id>``` 
- to come out of a tmux session: hit control-B keys and then immediately hit D
