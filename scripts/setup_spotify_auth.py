"""
Run this LOCALLY (not in Docker) once, with a browser available, to authorize
Spotify access. It writes data/spotify_token.json, which the sync service
then uses to silently refresh its access token forever.

Usage:
    pip install -r requirements.txt
    python scripts/setup_spotify_auth.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import spotipy  # noqa: E402
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth  # noqa: E402

SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"


def main() -> None:
    data_dir = os.environ.get("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    cache_path = os.path.join(data_dir, "spotify_token.json")

    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback"),
        scope=SCOPE,
        cache_handler=CacheFileHandler(cache_path=cache_path),
        open_browser=True,
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    me = sp.current_user()
    print(f"Authorized as {me['display_name']} ({me['id']})")
    print(f"Token cached at {cache_path} - copy this file's contents into your server's data/ volume.")


if __name__ == "__main__":
    main()
