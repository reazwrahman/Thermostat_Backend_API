# Project Overview
SmartHome uses raspberry pi as a primary microcontroller to operate a thermostat, control a 120V power relays which is connected to an electric heater and an air conditioner. This project uses concepts like multithreading and factory pattern to create reusable and maintable software. 

Attention: python version to use: 3.9


## Test Instruction for Target Hardware

- Navigate one directory up (where venv will be located) and create a backup folder 

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

