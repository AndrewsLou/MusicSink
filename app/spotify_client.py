import logging

import spotipy
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

log = logging.getLogger("spotify")

SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"


class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, cache_path: str, playlist_id: str):
        self.playlist_id = playlist_id
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SCOPE,
            cache_handler=CacheFileHandler(cache_path=cache_path),
            open_browser=False,
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlist_tracks(self) -> dict[str, dict]:
        """Returns {spotify_track_id: {id, name, artist}} for the current playlist contents."""
        tracks: dict[str, dict] = {}
        results = self.sp.playlist_items(
            self.playlist_id,
            additional_types=["track"],
            fields="items(track(id,name,artists(name))),next",
        )
        while results:
            for item in results.get("items", []):
                track = item.get("track")
                if not track or not track.get("id"):
                    continue
                artists = track.get("artists") or []
                tracks[track["id"]] = {
                    "id": track["id"],
                    "name": track["name"],
                    "artist": artists[0]["name"] if artists else "",
                }
            results = self.sp.next(results) if results.get("next") else None
        return tracks

    def search_track(self, artist: str, title: str) -> str | None:
        for query in (f"track:{title} artist:{artist}", f"{artist} {title}"):
            results = self.sp.search(q=query, type="track", limit=5)
            items = results.get("tracks", {}).get("items", [])
            if items:
                return items[0]["id"]
        return None

    def add_track(self, track_id: str) -> None:
        self.sp.playlist_add_items(self.playlist_id, [track_id])

    def remove_track(self, track_id: str) -> None:
        self.sp.playlist_remove_all_occurrences_of_items(self.playlist_id, [track_id])
