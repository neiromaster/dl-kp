import json
import os
import shutil
import subprocess
import configparser

import yaml

from utils.Config import Config
from utils.DownloadError import DownloadError
from utils.Downloader import Downloader
from utils.prompts import prompt_resume, prompt_params

DL_KP_CONFIG_FILE = "dl-kp.json"
YT_DLP_CONFIG_FILE = "dl-kp.yaml"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36"


def convert_to_mkv(config: Config):
    name = config.name
    audio = config.selected_audio
    subs = config.selected_subs

    audio_tracks = sum(
        [
            [
                "--default-track-flag",
                f"0:{1 if index == 0 else 0}",
                "--track-name",
                f"0:{track.name}",
                "--language",
                f"0:{track.language}",
                f"{name}/{name}-audio-{index}.mp4",
            ]
            for index, track in enumerate(audio)
        ],
        [],
    )
    subs_tracks = sum(
        [
            [
                "--default-track-flag",
                f"0:{1 if index == 0 else 0}",
                "--track-name",
                f"0:{track.name}",
                "--language",
                f"0:{track.language}",
                f"{name}/{name}-subs-{index}.mp4",
            ]
            for index, track in enumerate(subs)
        ],
        [],
    )

    command = (
        [
            "mkvmerge",
            "--stop-after-video-ends",
            "-o",
            f"{name}.mkv",
            f"{name}/{name}.mp4",
        ]
        + audio_tracks
        + subs_tracks
    )
    process = subprocess.run(command, text=True, check=True)

    print(process.stdout)


def save_settings(config):
    with open(DL_KP_CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file)


def load_settings() -> Config | None:
    if not os.path.exists(DL_KP_CONFIG_FILE):
        return None
    with open(DL_KP_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return Config().from_json(config)


def main():
    config = load_settings()
    if config:
        if not prompt_resume():
            os.remove(DL_KP_CONFIG_FILE)
            config = None

    with open("dl-kp.yaml", "r", encoding="utf-8") as file:
        dl_kp_config = yaml.safe_load(file)

    config = config if config else prompt_params(dl_kp_config["m3u8"]["http_headers"])

    save_settings(config.to_json())

    ydl = Downloader(config, yt_dlp_config=dl_kp_config["yt-dlp"])
    try:
        ydl.download()

        convert_to_mkv(config)

        if config.name:
            shutil.rmtree(config.name)
            os.remove(DL_KP_CONFIG_FILE)
    except DownloadError:
        print("Попробуйте перезапустить скрипт")
        exit(1)


if __name__ == "__main__":
    main()
