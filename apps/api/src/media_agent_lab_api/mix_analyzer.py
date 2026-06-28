from pathlib import Path

import numpy as np

from media_agent_lab_api.models import TrackAnalysis


KEY_NAMES = {
    "C": "Do",
    "C#": "Do thang",
    "D": "Re",
    "D#": "Re thang",
    "E": "Mi",
    "F": "Fa",
    "F#": "Fa thang",
    "G": "Sol",
    "G#": "Sol thang",
    "A": "La",
    "A#": "La thang",
    "B": "Si",
}

PITCH_CLASSES = list(KEY_NAMES)
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def analyze_mix(wav_path: Path) -> TrackAnalysis:
    import librosa

    audio, sr = librosa.load(wav_path, sr=None, mono=True)
    if audio.size == 0:
        raise ValueError("Cannot analyze empty audio")

    bpm = _estimate_bpm(audio, sr, librosa)
    key, scale = _estimate_key(audio, sr, librosa)
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
    rms = float(np.mean(librosa.feature.rms(y=audio)))
    tempo_bucket = _tempo_bucket(bpm)
    energy = _energy_bucket(rms)
    brightness = _brightness_bucket(centroid)
    key_vi = f"{KEY_NAMES[key]} {'truong' if scale == 'major' else 'thu'}"

    return TrackAnalysis(
        bpm=bpm,
        tempo_bucket=tempo_bucket,
        key=key,
        scale=scale,
        key_vi=key_vi,
        energy=energy,
        brightness=brightness,
        instrumentation=["full mix reference"],
        confidence={"bpm": 0.55 if bpm else 0.2, "key": 0.35, "instrumentation": 0.25},
    )


def _estimate_bpm(audio: np.ndarray, sr: int, librosa_module) -> int:
    try:
        tempo, _ = librosa_module.beat.beat_track(y=audio, sr=sr)
        return int(round(float(np.asarray(tempo).mean())))
    except Exception:
        return 0


def _estimate_key(audio: np.ndarray, sr: int, librosa_module) -> tuple[str, str]:
    chroma = librosa_module.feature.chroma_cqt(y=audio, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    if not np.any(chroma_mean):
        return "C", "major"

    major_scores = [_cosine(chroma_mean, np.roll(MAJOR_PROFILE, i)) for i in range(12)]
    minor_scores = [_cosine(chroma_mean, np.roll(MINOR_PROFILE, i)) for i in range(12)]
    major_idx = int(np.argmax(major_scores))
    minor_idx = int(np.argmax(minor_scores))
    if major_scores[major_idx] >= minor_scores[minor_idx]:
        return PITCH_CLASSES[major_idx], "major"
    return PITCH_CLASSES[minor_idx], "minor"


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _tempo_bucket(bpm: int) -> str:
    if bpm < 90:
        return "cham"
    if bpm <= 130:
        return "vua"
    return "nhanh"


def _energy_bucket(rms: float) -> str:
    if rms < 0.04:
        return "thap"
    if rms < 0.12:
        return "vua"
    return "cao"


def _brightness_bucket(centroid: float) -> str:
    if centroid < 1200:
        return "toi"
    if centroid < 2800:
        return "am"
    return "sang"
