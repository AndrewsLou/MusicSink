import logging
import time

from .config import Config
from .db import Database
from .spotify_client import SpotifyClient
from .sync import SyncEngine
from .ytmusic_client import YTMusicClient


def main() -> None:
    cfg = Config.from_env()
    logging.basicConfig(level=cfg.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log = logging.getLogger("main")

    db = Database(cfg.db_path)
    spotify = SpotifyClient(
        cfg.spotify_client_id,
        cfg.spotify_client_secret,
        cfg.spotify_redirect_uri,
        cfg.spotify_cache_path,
        cfg.spotify_playlist_id,
    )
    ytmusic = YTMusicClient(
        cfg.ytmusic_oauth_path,
        cfg.ytmusic_oauth_client_id,
        cfg.ytmusic_oauth_client_secret,
        cfg.ytmusic_playlist_id,
    )
    engine = SyncEngine(db, spotify, ytmusic)

    log.info("Starting playlist sync loop, checking every %ss", cfg.sync_interval_seconds)
    while True:
        try:
            engine.run()
        except Exception:
            log.exception("Sync run failed, will retry next interval")
        time.sleep(cfg.sync_interval_seconds)


if __name__ == "__main__":
    main()
