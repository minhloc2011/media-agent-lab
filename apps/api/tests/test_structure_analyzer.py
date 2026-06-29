from pathlib import Path

import numpy as np
import soundfile as sf

from media_agent_lab_api.structure_analyzer import analyze_structure


def test_analyze_structure_detects_rising_energy_curve(tmp_path: Path):
    sr = 22050
    third = sr
    audio = np.concatenate(
        [
            np.full(third, 0.02),
            np.full(third, 0.06),
            np.full(third, 0.18),
        ]
    )
    path = tmp_path / "mix.wav"
    sf.write(path, audio, sr)

    result = analyze_structure(path)

    assert result["energy_curve"] == "tang dan"
    assert result["chorus_lift"] == "manh"
    assert "điệp khúc" in result["section_hint"]
