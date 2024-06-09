### Requirements:

- For now only tested on Windows 11 and Linux Fedora 39 with python 3.11.4.

### Setup:

- copy and rename example.config.json to config.json and adjust the variables to your needs.
- run the following commands to init dependencies:

### windows:

- for virtual environment (you should use python 3.11.4): `python -m venv venv`

- to activate and use the environment: `.\venv\Scripts\activate`

- install dependencies `pip install -r requirements_windows.txt`

### linux:

- for virtual environment: `python3.11 -m venv venv`

- to activate and use the environment: `source venv/bin/activate`

- install dependencies `pip install -r requirements_linux.txt`

### Important:

- you need to install additional software on linux and maybe also on windows for the requirements to run correctly Unfortunately I can't remember exactly which ones I have installed on linux fedora, except the following:
- `sudo dnf install python3-devel portaudio-devel`

## How to Use:

- start recording by saying the startword or startkey
- interrupt assistent by saving the stopword or stopkey
- best practise by saying something before the startword or stopword and wait for a short moment. For example "okay ... [startword]"
- keeps conversation until next restart
