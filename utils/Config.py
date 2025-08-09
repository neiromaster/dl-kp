from __future__ import annotations
import dataclasses
import json
import os
from typing import List

from utils.Playlist import Video, AudioTrack, SubTrack


class Config:
    def __init__(self):
        self.link: str | None = None
        self.host: str | None = None
        self.name: str | None = None
        self.selected_video: Video | None = None
        self.selected_audio: List[AudioTrack] | None = None
        self.selected_subs: List[SubTrack] | None = None

    def from_json(self, data: dict):
        self.set_link(data.get("link"))
        self.set_name(data.get("name"))

        video_data = data.get("selected_video")
        if video_data:
            self.set_video(Video(**video_data))

        audio_data_list = data.get("selected_audio")
        if audio_data_list:
            self.set_audio([AudioTrack(**audio) for audio in audio_data_list])
        else:
            self.set_audio([])

        subs_data_list = data.get("selected_subs")
        if subs_data_list:
            self.set_subs([SubTrack(**sub) for sub in subs_data_list])
        else:
            self.set_subs([])

        return self

    def to_json(self):
        return {
            "link": self.link,
            "name": self.name,
            "selected_video": (
                dataclasses.asdict(self.selected_video) if self.selected_video else None
            ),
            "selected_audio": (
                [dataclasses.asdict(audio) for audio in self.selected_audio]
                if self.selected_audio
                else None
            ),
            "selected_subs": (
                [dataclasses.asdict(sub) for sub in self.selected_subs]
                if self.selected_subs
                else None
            ),
        }

    def save(self, filepath: str):
        with open(filepath, "w") as config_file:
            json.dump(self.to_json(), config_file)

    @classmethod
    def load(cls, filepath: str) -> "Config" | None:
        if not os.path.exists(filepath):
            return None
        with open(filepath) as config_file:
            config_data = json.load(config_file)
        return cls().from_json(config_data)

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
