from pathlib import Path

import numpy as np


def analyze_structure(wav_path: Path) -> dict[str, str]:
    import librosa

    audio, _ = librosa.load(wav_path, sr=None, mono=True)
    if audio.size == 0:
        raise ValueError("Cannot analyze empty audio structure")

    early, middle, late = _thirds(audio)
    energies = [_rms(part) for part in [early, middle, late]]
    energy_curve = _energy_curve(energies)
    chorus_lift = _chorus_lift(energies)
    section_hint = _section_hint(energy_curve, chorus_lift)

    return {
        "energy_curve": energy_curve,
        "section_hint": section_hint,
        "chorus_lift": chorus_lift,
    }


def _thirds(audio: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    parts = np.array_split(audio, 3)
    return parts[0], parts[1], parts[2]


def _rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def _energy_curve(energies: list[float]) -> str:
    early, middle, late = energies
    if late > early * 1.8 and middle >= early * 1.1:
        return "tang dan"
    if middle > early * 1.5 and late > early * 1.5:
        return "cao trao ro"
    if late < early * 0.7:
        return "giam dan"
    return "giu deu"


def _chorus_lift(energies: list[float]) -> str:
    early, _, late = energies
    if early <= 0:
        return "vua"
    ratio = late / early
    if ratio >= 2.4:
        return "manh"
    if ratio >= 1.4:
        return "vua"
    return "nhe"


def _section_hint(energy_curve: str, chorus_lift: str) -> str:
    if energy_curve == "tang dan" and chorus_lift == "manh":
        return "verse tối giản, pre-chorus nâng dần, điệp khúc mở rộng rõ"
    if energy_curve in {"tang dan", "cao trao ro"}:
        return "verse giữ gọn, pre-chorus tạo đà, điệp khúc mở vừa phải"
    if energy_curve == "giam dan":
        return "đầu bài nổi bật hơn, cuối bài hạ năng lượng để giữ cảm xúc lắng"
    return "năng lượng giữ đều, điệp khúc cần hook rõ để tạo điểm nhớ"
