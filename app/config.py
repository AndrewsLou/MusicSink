import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str
    spotify_playlist_id: str

    ytmusic_playlist_id: str
    ytmusic_oauth_client_id: str
    ytmusic_oauth_client_secret: str

    sync_interval_seconds: int
    data_dir: str
    log_level: str

    @property
    def db_path(self) -> str:
        return os.path.join(self.data_dir, "sync.db")

    @property
    def spotify_cache_path(self) -> str:
        return os.path.join(self.data_dir, "spotify_token.json")

    @property
    def ytmusic_oauth_path(self) -> str:
        return os.path.join(self.data_dir, "ytmusic_oauth.json")

    @classmethod
    def from_env(cls) -> "Config":
        data_dir = os.environ.get("DATA_DIR", "./data")
        os.makedirs(data_dir, exist_ok=True)

        def required(name: str) -> str:
            value = os.environ.get(name)
            if not value:
                raise RuntimeError(f"Missing required environment variable: {name}")
            return value

        return cls(
            spotify_client_id=required("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=required("SPOTIFY_CLIENT_SECRET"),
            spotify_redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback"),
            spotify_playlist_id=required("SPOTIFY_PLAYLIST_ID"),
            ytmusic_playlist_id=required("YTMUSIC_PLAYLIST_ID"),
            ytmusic_oauth_client_id=required("YTMUSIC_OAUTH_CLIENT_ID"),
            ytmusic_oauth_client_secret=required("YTMUSIC_OAUTH_CLIENT_SECRET"),
            sync_interval_seconds=int(os.environ.get("SYNC_INTERVAL_SECONDS", "600")),
            data_dir=data_dir,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
