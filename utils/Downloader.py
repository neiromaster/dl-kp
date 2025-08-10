from typing import List

import yt_dlp

from utils.Config import Config
from utils.Playlist import AudioTrack, SubTrack, Video
from utils.retry import retry


class Downloader:
    def __init__(self, config: Config, yt_dlp_config: dict):
        self.name: str = config.name
        self.selected_video: Video | None = config.selected_video
        self.selected_audio: List[AudioTrack] | None = config.selected_audio
        self.selected_subs: List[SubTrack] | None = config.selected_subs

        self.options: dict = yt_dlp_config
        self.downloader = yt_dlp.YoutubeDL(self.options)

    def _download_item(self, url: str, output_template: str) -> None:
        original_outtmpl = self.downloader.params.get("outtmpl")
        try:
            self.downloader.params["outtmpl"] = output_template
            retry(max_attempts=10, func=self.downloader.download, url_list=[url])
        finally:
            if original_outtmpl is not None:
                self.downloader.params["outtmpl"] = original_outtmpl
            elif "outtmpl" in self.downloader.params:
                del self.downloader.params["outtmpl"]

    def download_video(self, video: Video) -> None:
        output_template = f"{self.name}/{self.name}.mp4"
        self._download_item(video.url, output_template)

    def download_audio(self, audio_tracks: List[AudioTrack]) -> None:
        for index, track in enumerate(audio_tracks):
            output_template = f"{self.name}/{self.name}-audio-{index}.mp4"
            self._download_item(track.url, output_template)

    def download_subs(self, subs_tracks: List[SubTrack]) -> None:
        for index, track in enumerate(subs_tracks):
            output_template = f"{self.name}/{self.name}-subs-{index}.mp4"
            self._download_item(track.url, output_template)

    def download(self) -> None:
        if self.selected_video:
            self.download_video(self.selected_video)
        if self.selected_audio:
            self.download_audio(self.selected_audio)
        if self.selected_subs:
            self.download_subs(self.selected_subs)
