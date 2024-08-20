# Conversational Interface for IoT Devices

This project contains code for the demonstration paper for IoT 2024.

# Requirements
See requirements.txt file.

# Usage
1. Clone this repo

2. Install dependencies (recommended to use virtual environment conda)

```
conda create --name virtual_env_name
conda activate virtual_env_name
pip install -r requirements.txt
```


3. Pair IoT devices
Connect Philips Hue smart lamp to local machine via bluetooth.


4. Run Rasa action server

```
rasa run actions
```

5. Run Rasa dialogue shell

```
rasa shell
```




