import re
from dataclasses import dataclass, field
from urllib.parse import urlparse, urlunsplit

import m3u8
from yt_dlp.utils import urljoin

LANGUAGE_PATTERN = r"\(([A-Z]{3})\)"


class Playlist:
    def __init__(self, link: str, headers: dict = None):
        self._subs = None
        self._audios = None
        self._videos = None
        self._host: str | None = None

        self.headers = headers
        self.link = link
        self.get_playlist_info()

    def get_playlist_info(self):
        playlist = m3u8.load(self.link, headers=self.headers)
        self._videos = playlist.data.get("playlists", None)
        self._host = self.extract_host_from_video()

        media = playlist.data.get("media", [])

        self._audios = [track for track in media if track["type"] == "AUDIO"]
        self._subs = [track for track in media if track["type"] == "SUBTITLES"]

    def extract_host_from_video(self):
        return get_playlist_host(self.videos[0].url)

    @property
    def videos(self):
        return (
            [convert_to_video(video) for video in self._videos]
            if self._videos
            else None
        )

    @property
    def audios(self):
        return (
            [convert_to_audio(audio) for audio in self._audios]
            if self._audios
            else None
        )

    @property
    def subs(self):
        return (
            [convert_to_sub(sub, self._host) for sub in self._subs]
            if self._subs
            else None
        )


@dataclass
class Video:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self):
        return self.name


def convert_to_video(m3u8_playlist_entry) -> Video:
    if not m3u8_playlist_entry:
        raise ValueError("m3u8_playlist_entry is None")
    stream_info = m3u8_playlist_entry["stream_info"]
    return Video(
        name=stream_info["resolution"],
        group_id=stream_info["audio"],
        url=m3u8_playlist_entry["uri"],
    )


@dataclass
class AudioTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self):
        return f"{self.name} ({self.group_id})"

    @property
    def language(self):
        result = re.search(LANGUAGE_PATTERN, self.name)

        return result.group(1).lower() if result else "und"


def convert_to_audio(m3u8_media_entry) -> AudioTrack:
    if not m3u8_media_entry:
        raise ValueError("m3u8_media_entry is None")
    return AudioTrack(
        name=m3u8_media_entry["name"],
        group_id=m3u8_media_entry["group_id"],
        url=m3u8_media_entry["uri"],
    )


@dataclass
class SubTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self):
        return self.name

    @property
    def language(self):
        return self.name[:3].lower()


def convert_to_sub(m3u8_media_entry, host: str) -> SubTrack:
    if not m3u8_media_entry:
        raise ValueError("m3u8_media_entry is None")
    return SubTrack(
        name=m3u8_media_entry["name"],
        group_id=m3u8_media_entry["group_id"],
        url=urljoin(host, m3u8_media_entry["uri"]),
    )


def get_playlist_host(link: str) -> str:
    parsed_url = urlparse(link)
    host = urlunsplit((parsed_url.scheme, parsed_url.netloc, "", "", ""))

    return host
