import logging

from ytmusicapi import OAuthCredentials, YTMusic

log = logging.getLogger("ytmusic")


class YTMusicClient:
    def __init__(self, oauth_path: str, oauth_client_id: str, oauth_client_secret: str, playlist_id: str):
        self.playlist_id = playlist_id
        self.yt = YTMusic(
            oauth_path,
            oauth_credentials=OAuthCredentials(client_id=oauth_client_id, client_secret=oauth_client_secret),
        )

    def get_playlist_tracks(self) -> dict[str, dict]:
        """Returns {video_id: {id, name, artist, set_video_id}} for the current playlist contents.

        set_video_id is required by the YouTube Music API to remove a specific
        item from a playlist (a plain videoId is not enough).
        """
        tracks: dict[str, dict] = {}
        playlist = self.yt.get_playlist(self.playlist_id, limit=None)
        for item in playlist.get("tracks", []):
            video_id = item.get("videoId")
            if not video_id:
                continue
            artists = item.get("artists") or []
            tracks[video_id] = {
                "id": video_id,
                "name": item.get("title", ""),
                "artist": artists[0]["name"] if artists else "",
                "set_video_id": item.get("setVideoId"),
            }
        return tracks

    def search_track(self, artist: str, title: str) -> str | None:
        query = f"{artist} {title}"
        for filter_ in ("songs", "videos"):
            results = self.yt.search(query, filter=filter_, limit=5)
            if results and results[0].get("videoId"):
                return results[0]["videoId"]
        return None

    def add_track(self, video_id: str) -> None:
        self.yt.add_playlist_items(self.playlist_id, [video_id], duplicates=False)

    def remove_track(self, video_id: str, set_video_id: str | None) -> None:
        if not set_video_id:
            log.warning("Missing setVideoId for %s, cannot remove from YouTube Music playlist", video_id)
            return
        self.yt.remove_playlist_items(self.playlist_id, [{"videoId": video_id, "setVideoId": set_video_id}])
