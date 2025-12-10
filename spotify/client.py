# spotify/client.py

import base64
import requests
from urllib.parse import urlparse
from utils import get_logger
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

logger = get_logger("spotify")


class SpotifyClient:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    TRACK_URL_TEMPLATE = "https://api.spotify.com/v1/tracks/{track_id}"

    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        self.client_id = client_id or SPOTIFY_CLIENT_ID
        self.client_secret = client_secret or SPOTIFY_CLIENT_SECRET
        self.access_token = None

        if not self.client_id or not self.client_secret:
            logger.warning(
                "[spotify] Client ID/Secret not set. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your environment."
            )

    def _get_access_token(self):
        if self.access_token:
            return self.access_token

        logger.info("[spotify] Fetching access token...")

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials"
        }

        resp = requests.post(self.TOKEN_URL, headers=headers, data=data)

        if resp.status_code != 200:
            raise RuntimeError(
                f"[spotify] Failed to get token: {resp.status_code} {resp.text}"
            )

        token_info = resp.json()
        self.access_token = token_info["access_token"]
        logger.info("[spotify] Access token acquired.")
        return self.access_token

    @staticmethod
    def parse_track_id_from_url(spotify_url: str) -> str:
        """
        Extract track ID from a Spotify track URL like:
        https://open.spotify.com/track/<id>?...
        """
        parsed = urlparse(spotify_url)
        parts = parsed.path.split("/")
        # path format: /track/<id>
        if len(parts) >= 3 and parts[1] == "track":
            return parts[2]
        raise ValueError(f"Invalid Spotify track URL: {spotify_url}")

    def get_track_info(self, spotify_url: str) -> dict:
        """
        Fetch track info from Spotify Web API.

        Returns dict:
            {
              "id": track_id,
              "title": name,
              "artist": first artist name,
              "album": album name,
              "duration_ms": duration_ms
            }
        """
        track_id = self.parse_track_id_from_url(spotify_url)

        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }
        url = self.TRACK_URL_TEMPLATE.format(track_id=track_id)

        logger.info(f"[spotify] Fetching track info for track_id={track_id}")
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError(
                f"[spotify] Failed to get track info: {resp.status_code} {resp.text}"
            )

        data = resp.json()

        title = data.get("name", "Unknown Title")
        artists = data.get("artists", [])
        artist_name = artists[0]["name"] if artists else "Unknown Artist"
        album_name = data.get("album", {}).get("name", "")

        duration_ms = data.get("duration_ms", 0)

        info = {
            "id": track_id,
            "title": title,
            "artist": artist_name,
            "album": album_name,
            "duration_ms": duration_ms,
        }

        logger.info(
            f"[spotify] Track: '{title}' by '{artist_name}' "
            f"(album='{album_name}', duration_ms={duration_ms})"
        )

        return info
