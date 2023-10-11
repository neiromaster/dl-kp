import dataclasses
from typing import List

from utils.Playlist import Video, AudioTrack, SubTrack


class Config:
    def __init__(self):
        self.link: str | None = None
        self.name: str | None = None
        self.selected_video: Video | None = None
        self.selected_audio: List[AudioTrack] | None = None
        self.selected_subs: List[SubTrack] | None = None

    def from_json(self, config):
        self.link = config.get('link')
        self.name = config.get('name')
        self.selected_video = Video(**config.get('selected_video', {}))
        self.selected_audio = [AudioTrack(**audio)
                               for audio in config.get('selected_audio', []) or []]
        self.selected_subs = [SubTrack(**sub) for sub in config.get('selected_subs', []) or []]
        return self

    def to_json(self):
        return {
            'link': self.link,
            'name': self.name,
            'selected_video': dataclasses.asdict(self.selected_video) if self.selected_video else None,
            'selected_audio': [dataclasses.asdict(audio)
                               for audio in self.selected_audio] if self.selected_audio else None,
            'selected_subs': [dataclasses.asdict(sub) for sub in self.selected_subs] if self.selected_subs else None
        }

    def set_link(self, link: str):
        self.link = link

    def set_name(self, name: str):
        self.name = name

    def set_video(self, video: Video):
        self.selected_video = video

    def set_audio(self, audio: List[AudioTrack]):
        self.selected_audio = audio

    def set_subs(self, subs: List[SubTrack]):
        self.selected_subs = subs
