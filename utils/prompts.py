from typing import List

import questionary

from utils.Config import Config
from utils.Playlist import Playlist, Video, AudioTrack, SubTrack

RESUME_PROMPT = 'Найдена незаконченная загрузка. Продолжить?'
LINK_PROMPT = 'Введите ссылку: '
NAME_PROMPT = 'Введите название: '

RESOLUTION_PROMPT = 'Выберите разрешение'
AUDIO_PROMPT = 'Выберите аудио'
SUBS_PROMPT = 'Выберите субтитры'

YES_ANSWER = 'Да'
NO_ANSWER = 'Нет'


def prompt_resume():
    resume = questionary.select(
        'resume',
        message=RESUME_PROMPT,
        choices=[
            YES_ANSWER,
            NO_ANSWER
        ],
        default=YES_ANSWER
    ).ask()

    return resume == YES_ANSWER


def prompt_playlist_link() -> str:
    link = questionary.text(LINK_PROMPT).ask()
    print(link)
    return link.replace("\\", "")


def prompt_video_name():
    name = questionary.text(NAME_PROMPT).ask()
    return name


def prompt_video_params(video_list: List[Video]) -> (str, Video):
    choices = [questionary.Choice(video.view, value=video) for video in video_list]
    answer = questionary.select('Please select a video resolution:', choices=choices).ask()

    return answer


def prompt_audio_tracks(audio_list: List[AudioTrack], video: Video, selected_audio: List[AudioTrack] | None) \
        -> (str, List[AudioTrack]):
    choices = [questionary.Choice(
        audio.view,
        value=audio,
        checked=audio.group_id == video.group_id and ('RUS' in audio.name or 'ENG' in audio.name))
        for audio in audio_list]

    answers = questionary.checkbox(
        AUDIO_PROMPT,
        choices=choices,
    ).ask()

    return answers


def prompt_subs_tracks(sub_list: List[SubTrack], selected_subs: List[SubTrack] | None) -> (str, List[SubTrack]):
    choices = [questionary.Choice(sub.view, value=sub, checked=sub.name.startswith(("RUS", "ENG"))) for sub in sub_list]

    answers = questionary.checkbox(
        SUBS_PROMPT,
        choices=choices,
    ).ask()

    return answers


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

    selected_audio = prompt_audio_tracks(playlist.audios, selected_video,
                                         config.selected_audio) if playlist.audios else None
    config.set_audio(selected_audio)

    selected_subs = prompt_subs_tracks(playlist.subs, config.selected_subs) if playlist.subs else None
    config.set_subs(selected_subs)

    return config
