# playlist-sync

Keeps a Spotify playlist and a YouTube Music playlist (on separate accounts)
in sync. Every ~10 minutes it checks both playlists: songs added on one
platform are looked up (by artist + title) and added to the other; songs
removed from one are removed from the other too. A local SQLite database
records the Spotify-track-ID <-> YouTube-video-ID mapping for every synced
song, so it knows what it's responsible for.

## How it works

- **Spotify** access uses the official Web API (via `spotipy`) with a normal
  OAuth Authorization Code flow.
- **YouTube Music** access uses `ytmusicapi`'s OAuth device-code flow (the
  official YouTube Data API doesn't do song-accurate search/playlist editing
  the way YouTube Music's own API does).
- Both clients cache their **refresh token** to a file. Refresh tokens don't
  expire from use, so once you've authorized once (interactively, with a
  browser), the background service can keep renewing access tokens forever
  without any further human interaction — which is what makes it possible to
  run unattended on a headless server.
- On the very first run (empty database) it reconciles the two playlists:
  songs that already exist on both sides are matched up (by normalized
  artist+title) so they don't get duplicated. Anything left over is treated
  as new and synced across.

## 1. Create credentials

**Spotify**
1. Create an app at https://developer.spotify.com/dashboard.
2. Add `http://127.0.0.1:8080/callback` (or your own choice) as a Redirect URI.
3. Note the Client ID and Client Secret.

**YouTube Music**
1. In [Google Cloud Console](https://console.cloud.google.com/apis/library), enable the **YouTube Data API v3** on a project.
2. Under **APIs & Services > Credentials**, create an **OAuth client ID** of type **TVs and Limited Input devices**.
3. Note the Client ID and Client Secret.

Copy `.env.example` to `.env` and fill in both sets of credentials, plus the
`SPOTIFY_PLAYLIST_ID` and `YTMUSIC_PLAYLIST_ID` of the two playlists you want
kept in sync (the ID is the last path segment of the playlist's share link).

## 2. Authorize once (locally, with a browser)

These two scripts are interactive and need a browser — run them on your own
machine, not on the server:

```bash
pip install -r requirements.txt
python scripts/setup_spotify_auth.py
python scripts/setup_ytmusic_auth.py
```

Each writes a token file into `./data/`. Those files (plus the SQLite DB
that gets created on first run) are everything the service needs — copy the
whole `data/` folder to your server.

## 3. Run

```bash
docker compose up -d --build
```

The `data/` folder is mounted as a volume, so the SQLite DB and cached
tokens persist across restarts/redeploys. Logs: `docker compose logs -f`.

## Configuration

All via `.env` / environment variables (see `.env.example`):

| Variable | Description |
|---|---|
| `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` | Spotify app credentials |
| `SPOTIFY_REDIRECT_URI` | Must match the app's redirect URI |
| `SPOTIFY_PLAYLIST_ID` | Playlist to sync |
| `YTMUSIC_OAUTH_CLIENT_ID` / `YTMUSIC_OAUTH_CLIENT_SECRET` | Google OAuth client (TV/limited input) |
| `YTMUSIC_PLAYLIST_ID` | Playlist to sync |
| `SYNC_INTERVAL_SECONDS` | Poll interval, default `600` (10 min) |
| `DATA_DIR` | Where the DB + tokens live, default `/data` in Docker |
| `LOG_LEVEL` | Default `INFO` |

## Notes / limitations

- Matching is done via each platform's own search using `"<artist> <title>"`;
  it isn't perfect for remixes, live versions, or obscure tracks — check the
  logs (`WARNING: No ... match for ...`) if a song doesn't show up.
- If both accounts' tokens are ever revoked, re-run the two setup scripts
  and replace the files in `data/`.
- Cheap hosting: this is a lightweight single-container polling service, so
  it comfortably runs on the smallest tier of any VPS (e.g. a $4-6/mo
  droplet/instance) or a free-tier always-on container host.
