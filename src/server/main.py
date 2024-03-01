# entrypoint check
from pathlib import Path
from src.server.command_handler import MediaCommandHandler
from src.server.spotify import Root
from flask import Flask, request, redirect, session
