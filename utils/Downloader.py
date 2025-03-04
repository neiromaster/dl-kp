import yt_dlp

from utils.Config import Config
from utils.retry import retry


class Downloader:
    def __init__(self, config: Config, yt_dlp_config: dict):
        self.name = config.name
        self.selected_video = config.selected_video
        self.selected_audio = config.selected_audio
        self.selected_subs = config.selected_subs

        self.options = yt_dlp_config

    def download_video(self, video):
        options = self.options
        output_template = f"{self.name}/{self.name}.mp4"
        ydl_opts = {**options, "outtmpl": output_template}
        downloader = yt_dlp.YoutubeDL(ydl_opts)
        retry(max_attempts=10, func=downloader.download, url_list=[video.url])

    def download_audio(self, audio):
        for index, track in enumerate(audio):
            output_template = f"{self.name}/{self.name}-audio-{index}.mp4"
            ydl_opts = {**self.options, "outtmpl": output_template}
            downloader = yt_dlp.YoutubeDL(ydl_opts)
            retry(max_attempts=10, func=downloader.download, url_list=[track.url])

    def download_subs(self, subs):
        for index, track in enumerate(subs):
            output_template = f"{self.name}/{self.name}-subs-{index}.mp4"
            ydl_opts = {
                **self.options,
                "outtmpl": output_template,
            }
            downloader = yt_dlp.YoutubeDL(ydl_opts)
            retry(max_attempts=10, func=downloader.download, url_list=[track.url])

    def download(self):
        self.download_video(self.selected_video)
        if self.selected_audio:
            self.download_audio(self.selected_audio)
        if self.selected_subs:
            self.download_subs(self.selected_subs)
