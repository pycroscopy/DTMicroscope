import subprocess
import os
import sys

def run_server_stem():
    """Function to run the DTMicroscope server."""
    # Get the path to the server.py file inside the package
    server_script = os.path.join(os.path.dirname(__file__), 'server', 'server_stem.py')

    # Construct the nohup command with the resolved path to the server.py
    command = f"nohup {sys.executable} {server_script} > server.log 2>&1 &"

    # Use subprocess to run the command
    subprocess.Popen(command, shell=True)

    print("Server started and running in the background. Logs are being written to server.log.")

def run_server_afm():
    """Function to run the DTMicroscope server."""
    # Get the path to the server.py file inside the package
    server_script = os.path.join(os.path.dirname(__file__), 'server', 'server_afm.py')

    # Construct the nohup command with the resolved path to the server.py
    command = f"nohup {sys.executable} {server_script} > server.log 2>&1 &"

    # Use subprocess to run the command
    subprocess.Popen(command, shell=True)

    print("Server started and running in the background. Logs are being written to server.log.")
        

