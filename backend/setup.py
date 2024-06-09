from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(5000)

executables = [Executable("main.py", icon="img/ai.ico", target_name="assisstant")]

options = {
    'build_exe': {
        'packages': ["srsly", "blis", "spacy", "deepspeed", "uvicorn"],
        'include_files': ["config.json", "temp_audio", "img", "wakeup.wav"],
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