# Not maintained anymore. Use Branch server-client

# Jarvis

Jarvis is your conversational assistant available as a console programm. It can be used all local.

For now only tested on Windows 11 with python 3.11.4. Recommended vram 8gb.

- Voice To Text 📝:

  - faster-whisper(local)
  - whisper
  - google gtts

- Brain 🧠:

  - ollama(local)
  - groq
  - chatGPT

- Text to Speech 💬:

  - piper (local)
  - xtts (local)
  - google gtts

## How to Use:

- start recording by saying the startword or startkey
- interrupt assistent by saving the stopword or stopkey
- best practise by saying something before the startword or stopword and wait for a short moment. For example "okay ... [startword]"
- keeps conversation until next restart

## Setup:

- install cuda on windows from https://developer.nvidia.com/cuda-downloads?target_os=Windows
- remove torch and torchvision from requirements.txt
- run the following commands to init dependencies:

  - for virtual environment: `python -m venv venv`

  - to activate and use the environment: `.\venv\Scripts\activate`

  - install dependencies `pip install -r requirements.txt`

  - use /cu121 if you installed cuda 12 or use /cu118 if you installed cuda 11:
    `pip install torch==2.2.1 torchvision --index-url 
https://download.pytorch.org/whl/cu121`

- all settings like path to models (whisper, piper and xtts) can be specified in config.json

- copy and rename example.config.json to config.json

## Where to get models from?

- https://github.com/SYSTRAN/faster-whisper
- https://github.com/rhasspy/piper
- https://huggingface.co/coqui/XTTS-v2

## All about Ollama:

- https://github.com/ollama/ollama
