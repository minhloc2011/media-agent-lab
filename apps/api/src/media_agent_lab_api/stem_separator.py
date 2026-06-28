import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


Runner = Callable[[list[str]], None]


@dataclass(frozen=True)
class StemPaths:
    vocals: Path
    drums: Path
    bass: Path
    other: Path


def _default_runner(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True, text=True)


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
            "--device",
            self.device,
            "--name",
            self.model_name,
            "--out",
            str(work_dir),
            str(wav_path),
        ]
        self.runner(command)

        produced_root = work_dir / self.model_name / wav_path.stem
        outputs: dict[str, Path] = {}
        for stem in ["vocals", "drums", "bass", "other"]:
            source = produced_root / f"{stem}.wav"
            if not source.exists():
                raise RuntimeError(f"Demucs did not create expected stem: {source}")
            target = stems_dir / f"{stem}.wav"
            shutil.copyfile(source, target)
            outputs[stem] = target
        return StemPaths(**outputs)


def _default_device() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ModuleNotFoundError:
        return "cpu"
