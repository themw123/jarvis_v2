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

- download backend.7z from Releases
- extract it anywhere you want.
- rename example.config.json to config.json and adjust the variables to your needs.
- double click assisstant.exe
- now backend should be running and wait for client to connect

## Setup - Development:

- rename example.config.json to config.json and adjust the variables to your needs.

- run the following commands to init dependencies:

  - for virtual environment: `python -m venv venv`

  - to activate and use the environment: `.\venv\Scripts\activate`

  - adjust torch and torchvision in requirements.txt. /cu121 if you installed cuda 12 or use /cu118 if you installed cuda 11:

    ```
    torch==2.2.1 --index-url https://download.pytorch.org/whl/cu121
    torchvision --index-url https://download.pytorch.org/whl/cu121
    ```

  - install dependencies `pip install -r requirements.txt`

  - change transformers version(bug): `pip install transformers==4.40.1`
