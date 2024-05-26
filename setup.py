from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(5000)

# Die ausführbare Datei (EXE) soll erstellt werden
executables = [Executable("main.py", icon="img/ai.ico", target_name="assisstant")]

# Weitere Optionen (optional)
options = {
    'build_exe': {
        'packages': ["dns"],
        'include_files': ["config.json", "sound", "img"],  # Liste der zusätzlich einzuschließenden Dateien
        'excludes': [],       # Liste von Modulen, die nicht eingeschlossen werden sollen
    }
}

# Setup-Funktion aufrufen
setup(
    name="Assisstant",  # Name der Anwendung
    version="1.0",          # Versionsnummer
    description="assisstant",
    executables=executables,
    options=options
)