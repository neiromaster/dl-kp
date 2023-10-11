import json
import os
import shutil
import subprocess

from utils.DownloadError import DownloadError
from utils.Config import Config
from utils.YtDLP import YtDLP
from utils.prompts import prompt_resume, prompt_params


def convert_to_mkv(config: Config):
    name = config.name
    audio = config.selected_audio
    subs = config.selected_subs

    audio_tracks = sum(
        [['--track-name', f'0:{track.name}', f'{name}/{name}-audio-{index}.mp4'] for index, track in
         enumerate(audio)],
        [])
    subs_tracks = sum(
        [['--track-name', f'0:{track.name}', f'{name}/{name}-subs-{index}.mp4'] for index, track in enumerate(subs)],
        [])

    command = ['mkvmerge', '-o', f'{name}.mkv', f'{name}/{name}.mp4'] + audio_tracks + subs_tracks
    process = subprocess.run(command, text=True, check=True)

    print(process.stdout)


def save_settings(config):
    with open('yt-dlp-kp.json', 'w') as config_file:
        json.dump(config, config_file)


def load_settings() -> Config | None:
    if not os.path.exists('yt-dlp-kp.json'):
        return None
    with open('yt-dlp-kp.json') as config_file:
        config = json.load(config_file)
    return Config().from_json(config)


def main():
    config = load_settings()
    if config:
        if not prompt_resume():
            os.remove('yt-dlp-kp.json')
            config = None

    config = config if config else prompt_params()

    save_settings(config.to_json())

    ydl = YtDLP(config)
    try:
        ydl.download()

        convert_to_mkv(config)

        if config.name:
            shutil.rmtree(config.name)
            os.remove('yt-dlp-kp.json')
    except DownloadError:
        print('Попробуйте перезапустить скрипт')
        exit(1)


if __name__ == '__main__':
    main()
