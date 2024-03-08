from getpass import getuser
import subprocess
import os


def is_spotify_running():
    # List current running processes
    tasks = subprocess.check_output(["tasklist"]).decode("utf-8", "ignore")
    # Check if Spotify is in the list
    return "Spotify.exe" in tasks


def start_spotify():
    # Path to Spotify application, adjust as needed
    spotify_path = f"C:\\Users\\{getuser()}\\AppData\\Roaming\\Spotify\\Spotify.exe"
    os.startfile(spotify_path)
