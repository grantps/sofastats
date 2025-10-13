import os
from pathlib import Path
from subprocess import Popen
from time import sleep
from webbrowser import open_new_tab

def serve():
    cwd = Path(__file__).parent
    os.chdir(cwd)
    Popen(f"panel serve ui.py", shell=True)
    sleep(2)
    open_new_tab("http://localhost:5006/ui")
