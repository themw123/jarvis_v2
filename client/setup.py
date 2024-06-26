import platform
from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(5000)

executables = [Executable("main.py", icon="img/ai.ico", target_name="assisstant")]


packages = ['pynput', 'Xlib'] if platform.system() != 'Windows' else ['pynput']

options = {
    'build_exe': {
        'packages': packages,
        'include_files': ["example.config.json", "sound", "img"],
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