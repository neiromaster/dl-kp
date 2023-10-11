from dataclasses import dataclass, field
from urllib.parse import urlparse, urlunsplit

import m3u8


class Playlist:
    def __init__(self, link: str):
        self._subs = None
        self._audios = None
        self._videos = None

        self.link = link
        self.get_playlist_info()

    def get_playlist_info(self):
        playlist = m3u8.load(self.link)
        self._videos = playlist.data.get('playlists', None)

        media = playlist.data.get('media', [])

        self._audios = [track for track in media if track['type'] == 'AUDIO']
        self._subs = [track for track in media if track['type'] == 'SUBTITLES']

    @property
    def videos(self):
        return [convert_to_video(video) for video in self._videos] if self._videos else None

    @property
    def audios(self):
        return [convert_to_audio(audio) for audio in self._audios] if self._audios else None

    @property
    def subs(self):
        return [convert_to_sub(sub) for sub in self._subs] if self._subs else None


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
        raise ValueError('m3u8_playlist_entry is None')
    stream_info = m3u8_playlist_entry['stream_info']
    return Video(
        name=stream_info['resolution'],
        group_id=stream_info['audio'],
        url=m3u8_playlist_entry['uri']
    )


@dataclass
class AudioTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self):
        return f"{self.name} ({self.group_id})"


def convert_to_audio(m3u8_media_entry) -> AudioTrack:
    if not m3u8_media_entry:
        raise ValueError('m3u8_media_entry is None')
    return AudioTrack(
        name=m3u8_media_entry['name'],
        group_id=m3u8_media_entry['group_id'],
        url=m3u8_media_entry['uri']
    )


@dataclass
class SubTrack:
    name: str
    group_id: str
    url: str = field(compare=False, repr=False, hash=False, default=None)

    @property
    def view(self):
        return self.name


def convert_to_sub(m3u8_media_entry) -> SubTrack:
    if not m3u8_media_entry:
        raise ValueError('m3u8_media_entry is None')
    return SubTrack(
        name=m3u8_media_entry['name'],
        group_id=m3u8_media_entry['group_id'],
        url=m3u8_media_entry['uri']
    )


def get_playlist_host(link: str) -> str:
    parsed_url = urlparse(link)
    host = urlunsplit((parsed_url.scheme, parsed_url.netloc, '', '', ''))

    return host
