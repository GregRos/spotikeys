from .client import create_client
from msilib.schema import Media
from pathlib import Path

from src.server.manager import MediaCommandHandler
from src.server.spotify.root import Root


root = Root(
    client_id="b996e2c82b574509bec24fbd11eda035",
    client_secret="2370df9b5a7840a183f44bbd795483fa",
    redirect_uri="http://localhost:12000"
)
handler = MediaCommandHandler(root, Path("./history.state"))

client = create_client(lamb)