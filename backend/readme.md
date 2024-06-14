## Requirements (Pre Build and Development):

- Pre Build only tested on Windows 11
- Development only tested on Windows 11 and python 3.11.4

## Setup (Pre Build and Development):

- install cuda on windows from https://developer.nvidia.com/cuda-downloads?target_os=Windows

- download and install the models you want to use(faster-whisper, piper and xtts-v2).

  https://github.com/SYSTRAN/faster-whisper
  https://github.com/rhasspy/piper
  https://huggingface.co/coqui/XTTS-v2

- install ollama and download at least one model within ollama
  https://github.com/ollama/ollama

## Setup - Pre Build

- download .zip from Releases
- extract it anywhere you want.
- open config.json and adjust the variables to your needs.
- double click assisstant.exe
- now backend should be running and wait for client to connect

## Setup - Development:

- copy and rename example.config.json to config.json and adjust the variables to your needs.

- remove "torch", "torchvision" and "deepspeed @ file://.." from requirements.txt
- run the following commands to init dependencies:

  - for virtual environment: `python -m venv venv`

  - to activate and use the environment: `.\venv\Scripts\activate`

  - install dependencies `pip install -r requirements.txt`

  - install deepspeed: `pip install deepspeed-0.14.0+ce78a63-cp311-cp311-win_amd64.whl`

  - use /cu121 if you installed cuda 12 or use /cu118 if you installed cuda 11:
    `pip install torch==2.2.1 torchvision --index-url 
https://download.pytorch.org/whl/cu121`

  - change transformers version(bug): `pip install transformers==4.40.1`
