import shutil
import subprocess
import sys
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from shutil import which


Runner = Callable[[list[str], dict[str, str] | None], None]


@dataclass(frozen=True)
class StemPaths:
    vocals: Path
    drums: Path
    bass: Path
    other: Path


def _default_runner(command: list[str], env: dict[str, str] | None = None) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    except subprocess.CalledProcessError as exc:
        details = "\n".join(
            part
            for part in [
                f"Demucs failed with exit code {exc.returncode}.",
                f"stdout:\n{exc.stdout}" if exc.stdout else "",
                f"stderr:\n{exc.stderr}" if exc.stderr else "",
            ]
            if part
        )
        raise RuntimeError(details) from exc


class DemucsStemSeparator:
    def __init__(
        self,
        device: str | None = None,
        model_name: str = "htdemucs",
        runner: Runner | None = None,
    ):
        self.device = device or _default_device()
        self.model_name = model_name
        self.runner = runner or _default_runner

    def separate(self, wav_path: Path, stems_dir: Path, work_dir: Path) -> StemPaths:
        stems_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            "-m",
            "demucs",
            "--mp3",
            "--device",
            self.device,
            "--name",
            self.model_name,
            "--out",
            str(work_dir),
            str(wav_path),
        ]
        env = _demucs_env()
        self.runner(command, env)

        produced_root = work_dir / self.model_name / wav_path.stem
        outputs: dict[str, Path] = {}
        for stem in ["vocals", "drums", "bass", "other"]:
            source = produced_root / f"{stem}.mp3"
            if not source.exists():
                raise RuntimeError(f"Demucs did not create expected stem: {source}")
            target = stems_dir / f"{stem}.mp3"
            shutil.copyfile(source, target)
            outputs[stem] = target
        return StemPaths(**outputs)


def _default_device() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ModuleNotFoundError:
        return "cpu"


def _demucs_env() -> dict[str, str]:
    env = os.environ.copy()
    if which("ffmpeg", path=env.get("PATH")) and which("ffprobe", path=env.get("PATH")):
        return env

    static_dir = _static_ffmpeg_dir()
    if static_dir is not None:
        env["PATH"] = os.pathsep.join([str(static_dir), env.get("PATH", "")])
        return env

    try:
        import static_ffmpeg

        static_ffmpeg.add_paths(weak=True)
        env["PATH"] = os.environ["PATH"]
        return env
    except Exception as exc:
        raise RuntimeError(
            "Demucs requires both ffmpeg and ffprobe. Install FFmpeg on PATH or "
            "pre-cache static-ffmpeg binaries."
        ) from exc


def _static_ffmpeg_dir() -> Path | None:
    try:
        from static_ffmpeg.run import get_platform_dir
    except ModuleNotFoundError:
        return None

    directory = Path(get_platform_dir())
    suffix = ".exe" if sys.platform == "win32" else ""
    if (directory / f"ffmpeg{suffix}").exists() and (directory / f"ffprobe{suffix}").exists():
        return directory
    return None
