import re
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse, urlunsplit

import m3u8
from yt_dlp.utils import urljoin

LANGUAGE_PATTERN = r"\(([A-Z]{3})\)"


class Playlist:
    def __init__(self, link: str, headers: Optional[dict] = None):
        self._subs: Optional[List[dict]] = None
        self._audios: Optional[List[dict]] = None
        self._videos: Optional[List[dict]] = None
        self._host: Optional[str] = None

        self.headers = headers
        self.link = link
        self.get_playlist_info()

    def get_playlist_info(self) -> None:
        playlist = m3u8.load(self.link, headers=self.headers, verify_ssl=False)
        self._videos = playlist.data.get("playlists")

        if self._videos:
            first_video_uri = self._videos[0].get("uri")
            if first_video_uri:
                self._host = get_playlist_host(first_video_uri)
            else:
                self._host = get_playlist_host(self.link)
        else:
            self._host = get_playlist_host(self.link)

        media = playlist.data.get("media", [])

        self._audios = [track for track in media if track.get("type") == "AUDIO"]
        self._subs = [track for track in media if track.get("type") == "SUBTITLES"]

    @property
    def videos(self) -> Optional[List[Video]]:
        return (
            [convert_to_video(video) for video in self._videos]
            if self._videos
            else None
        )

    @property
    def audios(self) -> Optional[List[AudioTrack]]:
        return (
            [convert_to_audio(audio) for audio in self._audios]
            if self._audios
            else None
        )

    @property
    def subs(self) -> Optional[List[SubTrack]]:
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
    def view(self) -> str:
        return self.name


def convert_to_video(m3u8_playlist_entry: dict) -> Video:
    if not m3u8_playlist_entry:
        raise ValueError("m3u8_playlist_entry is None")
    stream_info = m3u8_playlist_entry.get("stream_info")
    if not stream_info:
        raise ValueError("Missing 'stream_info' in m3u8 playlist entry")

    return Video(
        name=stream_info.get("resolution"),
        group_id=stream_info.get("audio"),
        url=m3u8_playlist_entry.get("uri"),
    )


@dataclass
class AudioTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self) -> str:
        return f"{self.name} ({self.group_id})"

    @property
    def language(self) -> str:
        result = re.search(LANGUAGE_PATTERN, self.name)

        return result.group(1).lower() if result else "und"


def convert_to_audio(m3u8_media_entry: dict) -> AudioTrack:
    if not m3u8_media_entry:
        raise ValueError("m3u8_media_entry is None")
    return AudioTrack(
        name=m3u8_media_entry.get("name"),
        group_id=m3u8_media_entry.get("group_id"),
        url=m3u8_media_entry.get("uri"),
    )


@dataclass
class SubTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self) -> str:
        return self.name

    @property
    def language(self) -> str:
        return self.name[:3].lower()


def convert_to_sub(m3u8_media_entry: dict, host: str) -> SubTrack:
    if not m3u8_media_entry:
        raise ValueError("m3u8_media_entry is None")
    return SubTrack(
        name=m3u8_media_entry.get("name"),
        group_id=m3u8_media_entry.get("group_id"),
        url=urljoin(host, m3u8_media_entry.get("uri")),
    )


def get_playlist_host(link: str) -> str:
    parsed_url = urlparse(link)
    host = urlunsplit((parsed_url.scheme, parsed_url.netloc, "", "", ""))

    return host
