from pathlib import Path

from media_agent_lab_api.stem_separator import DemucsStemSeparator


def test_demucs_stem_separator_builds_command_and_collects_stems(tmp_path: Path):
    calls: list[list[str]] = []
    envs: list[dict[str, str] | None] = []
    wav_path = tmp_path / "input.wav"
    wav_path.write_bytes(b"wav")

    demucs_out = tmp_path / "demucs-out"
    produced_root = demucs_out / "htdemucs" / "input"

    def fake_runner(command: list[str], env: dict[str, str] | None = None) -> None:
        calls.append(command)
        envs.append(env)
        produced_root.mkdir(parents=True, exist_ok=True)
        for stem in ["vocals", "drums", "bass", "other"]:
            (produced_root / f"{stem}.mp3").write_bytes(stem.encode())

    separator = DemucsStemSeparator(device="cuda", runner=fake_runner)
    stems_dir = tmp_path / "job" / "stems"

    stems = separator.separate(wav_path, stems_dir, demucs_out)

    assert stems.vocals.read_bytes() == b"vocals"
    assert stems.drums.read_bytes() == b"drums"
    assert stems.bass.read_bytes() == b"bass"
    assert stems.other.read_bytes() == b"other"
    assert calls[0][1:6] == ["-m", "demucs", "--mp3", "--device", "cuda"]
    assert str(wav_path) in calls[0]
    assert envs[0] is not None
