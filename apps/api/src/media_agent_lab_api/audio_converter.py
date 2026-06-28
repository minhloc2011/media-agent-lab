import subprocess
from collections.abc import Callable
from pathlib import Path


Runner = Callable[[list[str]], None]


def _default_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ModuleNotFoundError:
        return "ffmpeg"


def _default_runner(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True, text=True)


class AudioConverter:
    def __init__(self, ffmpeg_exe: str | None = None, runner: Runner | None = None):
        self.ffmpeg_exe = ffmpeg_exe or _default_ffmpeg_exe()
        self.runner = runner or _default_runner

    def convert_to_wav(self, source: Path, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.ffmpeg_exe,
            "-y",
            "-i",
            str(source),
            "-ar",
            "44100",
            "-ac",
            "2",
            str(target),
        ]
        self.runner(command)
        if not target.exists():
            raise RuntimeError(f"FFmpeg did not create expected WAV: {target}")
        return target
