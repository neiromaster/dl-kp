from pprint import pprint
from urllib.parse import urljoin

import yt_dlp
from utils.Config import Config
from utils.Playlist import get_playlist_host
from utils.retry import retry


class YtDLP:
    def __init__(self, config: Config):
        self.name = config.name
        self.host = get_playlist_host(config.link)
        self.selected_video = config.selected_video
        self.selected_audio = config.selected_audio
        self.selected_subs = config.selected_subs

        self.options = {
            'concurrent_fragment_downloads': 5,
            'skip_unavailable_fragments': False,
            'fragment_retries': 50,
            'retries': 50,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/103.0.0.0 Safari/537.36'
            }
        }
        pprint(self.options, indent=4)

    def download_video(self, video):
        options = self.options
        output_template = f"{self.name}/{self.name}.mp4"
        ydl_opts = {
            **options,
            'outtmpl': output_template
        }
        downloader = yt_dlp.YoutubeDL(ydl_opts)
        retry(max_attempts=10, func=downloader.download, url_list=[video.url])

    def download_audio(self, audio):
        for index, track in enumerate(audio):
            output_template = f"{self.name}/{self.name}-audio-{index}.mp4"
            ydl_opts = {
                **self.options,
                'outtmpl': output_template
            }
            downloader = yt_dlp.YoutubeDL(ydl_opts)
            retry(max_attempts=10, func=downloader.download, url_list=[track.url])

    def download_subs(self, subs):
        for index, track in enumerate(subs):
            output_template = f"{self.name}/{self.name}-subs-{index}.mp4"
            ydl_opts = {
                **self.options,
                'outtmpl': output_template,
            }
            downloader = yt_dlp.YoutubeDL(ydl_opts)
            retry(max_attempts=10, func=downloader.download, url_list=[urljoin(self.host, track.url)])

    def download(self):
        self.download_video(self.selected_video)
        if self.selected_audio:
            self.download_audio(self.selected_audio)
        if self.selected_subs:
            self.download_subs(self.selected_subs)
