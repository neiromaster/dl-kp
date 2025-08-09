import json
import os
import shutil
import subprocess
import sys
import configparser

import yaml

from utils.Config import Config
from utils.DownloadError import DownloadError
from utils.Downloader import Downloader
from utils.prompts import prompt_resume, prompt_params
from utils.system import check_dependencies
from utils.video import convert_to_mkv

YT_DLP_CONFIG_FILE = "dl-kp.yaml"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36"


def main():
    check_dependencies()
    config = Config.load()
    if config:
        if not prompt_resume():
            os.remove("dl-kp.json")
            config = None

    with open("dl-kp.yaml", "r", encoding="utf-8") as file:
        dl_kp_config = yaml.safe_load(file)

    config = config if config else prompt_params(dl_kp_config["m3u8"]["http_headers"])

    config.save()

    ydl = Downloader(config, yt_dlp_config=dl_kp_config["yt-dlp"])
    try:
        ydl.download()

        convert_to_mkv(config)

        if config.name:
            shutil.rmtree(config.name)
            os.remove("dl-kp.json")
    except DownloadError:
        print("Попробуйте перезапустить скрипт")
        exit(1)


if __name__ == "__main__":
    main()
