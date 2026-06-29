from pathlib import Path

import numpy as np

from media_agent_lab_api.models import VocalAnalysis


def analyze_vocal(vocal_path: Path) -> VocalAnalysis:
    import librosa

    audio, sr = librosa.load(vocal_path, sr=None, mono=True)
    if audio.size == 0:
        raise ValueError("Cannot analyze empty vocal stem")

    frame_length = 2048
    hop_length = 512
    rms_values = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    rms = float(np.mean(rms_values))
    active_mask = rms_values > max(0.01, rms * 0.45)
    active_ratio = float(np.mean(active_mask))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
    median_pitch, pitch_confidence, pitch_spread = _estimate_pitch(
        audio,
        sr,
        librosa,
        active_mask,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    range_bucket = _range_bucket(median_pitch, pitch_spread)
    brightness = _brightness_bucket(centroid)
    power = _power_bucket(rms)
    density = _density_bucket(active_ratio)
    presence = _presence_bucket(rms, centroid)
    phrasing = _phrasing_label(density)
    descriptor = _voice_descriptor(range_bucket, brightness, power)

    return VocalAnalysis(
        median_pitch_hz=round(median_pitch, 2),
        range_bucket=range_bucket,
        voice_descriptor=descriptor,
        brightness=brightness,
        power=power,
        density=density,
        phrasing=phrasing,
        presence=presence,
        confidence={
            "pitch": pitch_confidence,
            "range": 0.65 if pitch_spread > 0 else 0.35,
            "voice_descriptor": 0.6 if median_pitch > 0 else 0.35,
        },
    )


def _estimate_pitch(
    audio: np.ndarray,
    sr: int,
    librosa_module,
    active_mask: np.ndarray,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> tuple[float, float, float]:
    try:
        f0 = librosa_module.yin(
            audio,
            fmin=librosa_module.note_to_hz("C2"),
            fmax=librosa_module.note_to_hz("C6"),
            sr=sr,
            frame_length=frame_length,
            hop_length=hop_length,
        )
    except Exception:
        return 0.0, 0.0, 0.0

    frame_count = min(f0.size, active_mask.size)
    f0 = f0[:frame_count]
    mask = active_mask[:frame_count]
    voiced = f0[np.isfinite(f0) & mask]
    if voiced.size == 0:
        return 0.0, 0.0, 0.0

    spread = float(np.percentile(voiced, 90) - np.percentile(voiced, 10))
    confidence = float(np.mean(mask))
    return float(np.median(voiced)), round(confidence, 2), spread


def _range_bucket(median_pitch: float, pitch_spread: float) -> str:
    if median_pitch <= 0:
        return "khong ro"
    if median_pitch < 165:
        return "trung"
    if median_pitch < 280:
        return "trung-cao"
    return "cao"


def _brightness_bucket(centroid: float) -> str:
    if centroid < 1200:
        return "toi"
    if centroid < 2800:
        return "am"
    return "sang"


def _power_bucket(rms: float) -> str:
    if rms < 0.035:
        return "nhe"
    if rms < 0.1:
        return "vua"
    return "cao"


def _density_bucket(active_ratio: float) -> str:
    if active_ratio < 0.35:
        return "thoang"
    if active_ratio < 0.7:
        return "can bang"
    return "day"


def _presence_bucket(rms: float, centroid: float) -> str:
    if rms > 0.1 or centroid > 2800:
        return "noi bat"
    if rms < 0.035 and centroid < 1200:
        return "lui"
    return "can bang"


def _phrasing_label(density: str) -> str:
    if density == "thoang":
        return "câu hát có nhiều khoảng thở"
    if density == "day":
        return "câu hát dày, cần giữ vài khoảng nghỉ để lời mới rõ chữ"
    return "câu hát có khoảng thở tự nhiên"


def _voice_descriptor(range_bucket: str, brightness: str, power: str) -> str:
    if range_bucket == "khong ro":
        return "giọng hát chưa bắt được cao độ rõ, ưu tiên xử lý tự nhiên"
    brightness_vi = {"toi": "trầm ấm", "am": "ấm", "sang": "sáng"}[brightness]
    power_vi = {"nhe": "nhẹ", "vua": "vừa", "cao": "rõ lực"}[power]
    return f"giọng {range_bucket} {brightness_vi}, lực hát {power_vi}"
