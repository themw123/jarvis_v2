## Setup:

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
