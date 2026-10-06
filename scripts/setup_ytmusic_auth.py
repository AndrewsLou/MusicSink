"""
Run this LOCALLY (not in Docker) once, with a browser available, to authorize
YouTube Music access via Google's OAuth device flow. It writes
data/ytmusic_oauth.json, which the sync service then uses to silently
refresh its access token forever.

Requires a Google Cloud OAuth client of type "TVs and Limited Input devices"
(create one at https://console.cloud.google.com/apis/credentials after
enabling the "YouTube Data API v3" API on the project).

Usage:
    pip install -r requirements.txt
    python scripts/setup_ytmusic_auth.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from ytmusicapi import setup_oauth  # noqa: E402


def main() -> None:
    data_dir = os.environ.get("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "ytmusic_oauth.json")

    setup_oauth(
        client_id=os.environ["YTMUSIC_OAUTH_CLIENT_ID"],
        client_secret=os.environ["YTMUSIC_OAUTH_CLIENT_SECRET"],
        filepath=out_path,
        open_browser=True,
    )
    print(f"OAuth credentials saved to {out_path} - copy this file's contents into your server's data/ volume.")


if __name__ == "__main__":
    main()
