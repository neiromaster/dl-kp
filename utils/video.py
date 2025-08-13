import subprocess

from utils.Config import Config


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
            for index, track in enumerate(audio or [])
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
            for index, track in enumerate(subs or [])
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
