from cx_Freeze import setup, Executable
import sys
import os
sys.setrecursionlimit(5000)


if not os.path.exists('temp_audio'):
    os.makedirs('temp_audio')
open('temp_audio/.keep', 'a').close()
    
executables = [Executable("main.py", icon="img/ai.ico", target_name="assisstant")]

options = {
    'build_exe': {
        'packages': ["srsly", "blis", "spacy", "deepspeed", "uvicorn"],
        'include_files': ["example.config.json", "temp_audio", "img", "wakeup.wav"],
        'excludes': [],
    }
}

setup(
    name="Assisstant",
    version="1.0",
    description="assisstant",
    executables=executables,
    options=options
)