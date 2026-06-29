from pathlib import Path

import numpy as np
import soundfile as sf

from media_agent_lab_api.vocal_analyzer import _estimate_pitch, analyze_vocal


def test_analyze_vocal_returns_prompt_safe_vocal_detail(tmp_path: Path):
    sr = 22050
    t = np.linspace(0, 2.0, sr * 2, endpoint=False)
    audio = 0.18 * np.sin(2 * np.pi * 220.0 * t)
    path = tmp_path / "vocals.wav"
    sf.write(path, audio, sr)

    result = analyze_vocal(path)

    assert result.median_pitch_hz > 150
    assert result.range_bucket in {"trung", "trung-cao", "cao"}
    assert "giọng" in result.voice_descriptor
    assert result.density in {"thoang", "can bang", "day"}
    assert "câu hát" in result.phrasing
    assert result.presence in {"lui", "can bang", "noi bat"}
    assert "ca sĩ" not in result.voice_descriptor.lower()


def test_estimate_pitch_uses_fast_yin_frames():
    class FakeLibrosa:
        @staticmethod
        def note_to_hz(note: str) -> float:
            return {"C2": 65.4, "C6": 1046.5}[note]

        @staticmethod
        def yin(audio, fmin, fmax, sr, frame_length, hop_length):
            return np.array([110.0, 220.0, 221.0, 440.0])

    active_mask = np.array([False, True, True, False])

    median_pitch, confidence, spread = _estimate_pitch(
        np.zeros(4096),
        22050,
        FakeLibrosa(),
        active_mask,
    )

    assert round(median_pitch) == 220
    assert confidence == 0.5
    assert spread > 0
