import dataclasses
from typing import List

import inquirer

from utils.Config import Config
from utils.Playlist import Playlist, convert_to_video, convert_to_audio, Video, convert_to_sub, AudioTrack, SubTrack

RESUME_PROMPT = 'Найдена незаконченная загрузка. Продолжить?'
LINK_PROMPT = 'Введите ссылку: '
NAME_PROMPT = 'Введите название: '

RESOLUTION_PROMPT = 'Выберите разрешение'
AUDIO_PROMPT = 'Выберите аудио'
SUBS_PROMPT = 'Выберите субтитры'

YES_ANSWER = 'Да'
NO_ANSWER = 'Нет'


def prompt_resume():
    resume = [
        inquirer.List(
            'resume',
            message=RESUME_PROMPT,
            choices=[
                YES_ANSWER,
                NO_ANSWER
            ],
            default=YES_ANSWER
        )
    ]

    return inquirer.prompt(resume)['resume'] == YES_ANSWER


def prompt_playlist_link() -> str:
    link = input(LINK_PROMPT)
    return link.replace("\\", "")


def prompt_video_name():
    name = input(NAME_PROMPT)
    return name


def prompt_video_params(video_list: List[Video]) -> (str, Video):
    choices = [(video.view, video) for video in video_list]
    question = inquirer.List('video', message='Please select a video resolution:', choices=choices)

    answers = inquirer.prompt([question])
    return answers['video']


def prompt_audio_tracks(audio_list: List[AudioTrack], video: Video, selected_audio: List[AudioTrack] | None) \
        -> (str, List[AudioTrack]):
    choices = [(audio.view, audio) for audio in audio_list]

    if selected_audio:
        default_choices = [audio for audio in audio_list if audio in selected_audio]
    else:
        default_choices = [audio for audio in audio_list
                           if audio.group_id == video.group_id
                           and ('RUS' in audio.name or 'ENG' in audio.name)]

    questions = [
        inquirer.Checkbox(
            'audio',
            message=AUDIO_PROMPT,
            choices=choices,
            default=default_choices
        )
    ]

    answers = inquirer.prompt(questions)
    return answers['audio']


def prompt_subs_tracks(sub_list: List[SubTrack], selected_subs: List[SubTrack] | None) -> (str, List[SubTrack]):
    choices = [(sub.view, sub) for sub in sub_list]

    if selected_subs:
        default_choices = [sub for sub in sub_list if sub in selected_subs]
    else:
        default_choices = [sub for sub in sub_list
                           if sub.name.startswith(("RUS", "ENG"))]

    questions = [
        inquirer.Checkbox(
            'subs',
            message=SUBS_PROMPT,
            choices=choices,
            default=default_choices
        )
    ]

    answers = inquirer.prompt(questions)
    return answers['subs']


def prompt_params():
    config = Config()

    playlist_link = prompt_playlist_link()
    config.set_link(playlist_link)

    playlist = Playlist(playlist_link)
    video_name = prompt_video_name()
    config.set_name(video_name)

    selected_video = prompt_video_params(playlist.videos)
    config.set_video(selected_video)

    if not selected_video:
        exit(1)

    selected_audio = prompt_audio_tracks(playlist.audios, selected_video, config.selected_audio) if playlist.audios else None
    config.set_audio(selected_audio)

    selected_subs = prompt_subs_tracks(playlist.subs, config.selected_subs) if playlist.subs else None
    config.set_subs(selected_subs)

    return config
