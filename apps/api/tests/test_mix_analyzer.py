from pathlib import Path
from wave import open as wave_open

import numpy as np

from media_agent_lab_api.mix_analyzer import analyze_mix


def write_sine_wav(path: Path, frequency: float = 440.0, seconds: float = 1.0, sr: int = 22050) -> None:
    samples = np.sin(2 * np.pi * frequency * np.linspace(0, seconds, int(sr * seconds), endpoint=False))
    pcm = (samples * 32767).astype("<i2")
    with wave_open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(pcm.tobytes())


def test_analyze_mix_returns_prompt_safe_track_metadata(tmp_path: Path):
    wav_path = tmp_path / "tone.wav"
    write_sine_wav(wav_path)

    track = analyze_mix(wav_path)

    assert track.bpm >= 0
    assert track.tempo_bucket in {"cham", "vua", "nhanh"}
    assert track.key_vi.endswith(("truong", "thu"))
    assert track.energy in {"thap", "vua", "cao"}
    assert track.brightness in {"toi", "am", "sang"}
    assert track.instrumentation
    assert 0.0 <= track.confidence["bpm"] <= 1.0
