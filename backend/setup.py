from cx_Freeze import setup, Executable
import sys
import os
sys.setrecursionlimit(5000)

# Abrufen der Umgebungsvariablen
cuda_path = os.getenv('CUDA_PATH')
cuda_path_v12_3 = os.getenv('CUDA_PATH_V12_3')

print(f"CUDA_PATH: {cuda_path}")
print(f"CUDA_PATH_V12_3: {cuda_path_v12_3}")


if not os.path.exists('temp_audio'):
    os.makedirs('temp_audio')
open('temp_audio/.keep', 'a').close()
    
executables = [Executable("main.py", icon="img/ai.ico", target_name="assisstant")]

options = {
    'build_exe': {
        'include_msvcr': True,
        'packages': ["srsly", "blis", "spacy", "deepspeed", "uvicorn", "sklearn"],
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