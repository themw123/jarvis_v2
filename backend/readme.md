## Requirements:

- For now only tested on Windows 11 with python 3.11.4. Recommended vram 8gb.

## Setup:

- copy and rename example.config.json to config.json and adjust the variables to your needs.
- install cuda on windows from https://developer.nvidia.com/cuda-downloads?target_os=Windows
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

  - all settings like path to models (whisper, piper and xtts) can be specified in config.json

## Where to get models from?

- https://github.com/SYSTRAN/faster-whisper
- https://github.com/rhasspy/piper
- https://huggingface.co/coqui/XTTS-v2

## All about Ollama:

- https://github.com/ollama/ollama
