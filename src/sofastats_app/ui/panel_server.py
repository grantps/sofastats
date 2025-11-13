from collections.abc import Sequence
import os
from pathlib import Path
import subprocess
import threading
from time import sleep
from webbrowser import open_new_tab

def run_server():
    args = f"panel serve ui.py --static-dirs images=./images --session-token-expiration=900000"  ## https://discourse.bokeh.org/t/protocol-error-token-is-expired/11575
    subprocess.run(args, shell=True)

def speak(lines: Sequence[str]):
    print("")
    for line in lines:
        print(f"🐇 {line}")
    print("")

def serve():
    cwd = Path(__file__).parent
    try:
        os.chdir(cwd)
    except FileNotFoundError as e:
        speak(f"Can't change directory to '{cwd}' for some reason. Orig error: {e}")
    speak(["Hi there - just starting SOFA Stats", "Waiting a couple of seconds so everything's ready"])
    output_thread = threading.Thread(target=run_server)
    output_thread.start()
    sleep(2)  ## to give server time to be ready before tab opens
    open_new_tab("http://localhost:5006/ui")
    speak([
        "I just opened a new tab in your web browser with the SOFA Stats App - enjoy!",
        ("Don't worry about all the technical chatter below - "
        "it might become useful if SOFA Stats stops working properly for some reason."),
        ("To stop SOFA Stats, either close this window manually or, if you know how, "
        "use the command to stop this program running e.g. Ctrl-C"),
    ])
    output_thread.join()

if __name__ == '__main__':
    serve()
