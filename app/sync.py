import logging

from .db import Database
from .matcher import track_key
from .spotify_client import SpotifyClient
from .ytmusic_client import YTMusicClient

log = logging.getLogger("sync")


class SyncEngine:
    def __init__(self, db: Database, spotify: SpotifyClient, ytmusic: YTMusicClient):
        self.db = db
        self.spotify = spotify
        self.ytmusic = ytmusic

    def run(self) -> None:
        if self.db.is_empty():
            self._reconcile_initial()

        spotify_tracks = self.spotify.get_playlist_tracks()
        youtube_tracks = self.ytmusic.get_playlist_tracks()
        mappings = self.db.all_mappings()

        mapped_spotify_ids = {m["spotify_track_id"] for m in mappings if m["spotify_track_id"]}
        mapped_youtube_ids = {m["youtube_video_id"] for m in mappings if m["youtube_video_id"]}

        for spotify_id, info in spotify_tracks.items():
            if spotify_id not in mapped_spotify_ids:
                self._handle_new_spotify_track(info)

        for video_id, info in youtube_tracks.items():
            if video_id not in mapped_youtube_ids:
                self._handle_new_youtube_track(info)

        for mapping in mappings:
            if mapping["spotify_track_id"] and mapping["spotify_track_id"] not in spotify_tracks:
                self._handle_removed_from_spotify(mapping, youtube_tracks)
            elif mapping["youtube_video_id"] and mapping["youtube_video_id"] not in youtube_tracks:
                self._handle_removed_from_youtube(mapping)

    def _handle_new_spotify_track(self, info: dict) -> None:
        video_id = self.ytmusic.search_track(info["artist"], info["name"])
        if not video_id:
            log.warning("No YouTube Music match for %s - %s", info["artist"], info["name"])
            return
        try:
            self.ytmusic.add_track(video_id)
        except Exception:
            log.exception("Failed to add %s - %s to YouTube Music", info["artist"], info["name"])
            return
        self.db.insert_mapping(info["id"], video_id, info["artist"], info["name"], "spotify")
        log.info("Synced Spotify -> YouTube Music: %s - %s", info["artist"], info["name"])

    def _handle_new_youtube_track(self, info: dict) -> None:
        track_id = self.spotify.search_track(info["artist"], info["name"])
        if not track_id:
            log.warning("No Spotify match for %s - %s", info["artist"], info["name"])
            return
        try:
            self.spotify.add_track(track_id)
        except Exception:
            log.exception("Failed to add %s - %s to Spotify", info["artist"], info["name"])
            return
        self.db.insert_mapping(track_id, info["id"], info["artist"], info["name"], "youtube")
        log.info("Synced YouTube Music -> Spotify: %s - %s", info["artist"], info["name"])

    def _handle_removed_from_spotify(self, mapping, youtube_tracks: dict) -> None:
        video_id = mapping["youtube_video_id"]
        if video_id and video_id in youtube_tracks:
            set_video_id = youtube_tracks[video_id].get("set_video_id")
            try:
                self.ytmusic.remove_track(video_id, set_video_id)
                log.info("Removed from YouTube Music (deleted on Spotify): %s - %s", mapping["artist"], mapping["title"])
            except Exception:
                log.exception("Failed to remove %s - %s from YouTube Music", mapping["artist"], mapping["title"])
                return
        self.db.delete_mapping(mapping["id"])

    def _handle_removed_from_youtube(self, mapping) -> None:
        track_id = mapping["spotify_track_id"]
        if track_id:
            try:
                self.spotify.remove_track(track_id)
                log.info("Removed from Spotify (deleted on YouTube Music): %s - %s", mapping["artist"], mapping["title"])
            except Exception:
                log.exception("Failed to remove %s - %s from Spotify", mapping["artist"], mapping["title"])
                return
        self.db.delete_mapping(mapping["id"])

    def _reconcile_initial(self) -> None:
        """First-run baseline: match songs that already exist on both playlists
        (by normalized artist+title) so they aren't duplicated across platforms.
        Anything left unmatched is picked up as a normal new-track sync afterwards."""
        log.info("Empty database detected - performing initial reconciliation")
        spotify_tracks = self.spotify.get_playlist_tracks()
        youtube_tracks = self.ytmusic.get_playlist_tracks()

        youtube_by_key: dict[str, str] = {}
        for video_id, info in youtube_tracks.items():
            youtube_by_key.setdefault(track_key(info["artist"], info["name"]), video_id)

        matched = 0
        for spotify_id, info in spotify_tracks.items():
            video_id = youtube_by_key.get(track_key(info["artist"], info["name"]))
            if video_id:
                self.db.insert_mapping(spotify_id, video_id, info["artist"], info["name"], "reconcile")
                matched += 1
        log.info("Initial reconciliation matched %d existing tracks across both playlists", matched)
