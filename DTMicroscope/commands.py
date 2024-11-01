import subprocess
import os
import sys

<<<<<<< HEAD
def run_server():
    """Function to run the DTMicroscope server."""
    # Get the path to the server.py file inside the package
    server_script = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
=======
def run_server_stem():
    """Function to run the DTMicroscope server."""
    # Get the path to the server.py file inside the package
    server_script = os.path.join(os.path.dirname(__file__), 'server_stem', 'server_stem.py')
>>>>>>> f1925882f2f99d002e281c3319573194503fc40e

    # Construct the nohup command with the resolved path to the server.py
    command = f"nohup {sys.executable} {server_script} > server.log 2>&1 &"

    # Use subprocess to run the command
    subprocess.Popen(command, shell=True)

    print("Server started and running in the background. Logs are being written to server.log.")
<<<<<<< HEAD
=======
        
def run_server_afm():
    """Function to run the DTMicroscope server."""
    # Get the path to the server.py file inside the package
    server_script = os.path.join(os.path.dirname(__file__), 'server_afm', 'server_afm.py')

    # Construct the nohup command with the resolved path to the server.py
    command = f"nohup {sys.executable} {server_script} > server.log 2>&1 &"

    # Use subprocess to run the command
    subprocess.Popen(command, shell=True)

    print("Server started and running in the background. Logs are being written to server.log.")
        
>>>>>>> f1925882f2f99d002e281c3319573194503fc40e
