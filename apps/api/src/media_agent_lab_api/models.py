from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    CONVERTING = "converting"
    SEPARATING_STEMS = "separating_stems"
    ANALYZING_MIX = "analyzing_mix"
    ANALYZING_VOCAL = "analyzing_vocal"
    DETECTING_LANGUAGE = "detecting_language"
    GENERATING_PROMPT = "generating_prompt"
    COMPLETED = "completed"
    FAILED_VALIDATION = "failed_validation"
    FAILED_CONVERT = "failed_convert"
    FAILED_DEMUCS = "failed_demucs"
    FAILED_MIX_ANALYSIS = "failed_mix_analysis"
    FAILED_VOCAL_ANALYSIS = "failed_vocal_analysis"
    FAILED_LANGUAGE_DETECTION = "failed_language_detection"
    FAILED_PROMPT_GENERATION = "failed_prompt_generation"


class JobRecord(BaseModel):
    id: str
    status: JobStatus
    original_filename: str
    created_at: datetime
    updated_at: datetime
    error_code: str | None = None
    error_message: str | None = None


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    current_step: str
    error_code: str | None = None
    error_message: str | None = None


class TrackAnalysis(BaseModel):
    bpm: int
    tempo_bucket: str
    key: str
    scale: str
    key_vi: str
    energy: str
    brightness: str
    instrumentation: list[str]
    confidence: dict[str, float]
    energy_curve: str = "giu deu"
    section_hint: str = "verse tối giản, điệp khúc mở rộng"
    chorus_lift: str = "vua"


class VocalAnalysis(BaseModel):
    median_pitch_hz: float
    range_bucket: str
    voice_descriptor: str
    brightness: str
    power: str
    confidence: dict[str, float]
    density: str = "can bang"
    phrasing: str = "câu hát có khoảng thở tự nhiên"
    presence: str = "can bang"


class LanguageAnalysis(BaseModel):
    detected: str | None = None
    label_vi: str | None = None
    confidence: float = 0.0
    used_in_prompt: bool = False


class PromptResult(BaseModel):
    tags_vi: str
    omitted_fields: list[str]
    warnings: list[str]


class AnalysisResult(BaseModel):
    track: TrackAnalysis
    vocal: VocalAnalysis
    language: LanguageAnalysis = Field(default_factory=LanguageAnalysis)
    prompt: PromptResult


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def status_progress(status: JobStatus) -> tuple[int, str]:
    mapping: dict[JobStatus, tuple[int, str]] = {
        JobStatus.UPLOADED: (5, "Da nhan file"),
        JobStatus.VALIDATING: (12, "Dang kiem tra file"),
        JobStatus.CONVERTING: (24, "Dang chuan hoa am thanh"),
        JobStatus.SEPARATING_STEMS: (42, "Dang tach stem"),
        JobStatus.ANALYZING_MIX: (58, "Dang phan tich ban mix"),
        JobStatus.ANALYZING_VOCAL: (72, "Dang phan tich giong hat"),
        JobStatus.DETECTING_LANGUAGE: (82, "Dang nhan dien ngon ngu"),
        JobStatus.GENERATING_PROMPT: (92, "Dang tao prompt"),
        JobStatus.COMPLETED: (100, "Hoan thanh"),
    }
    if status.value.startswith("failed_"):
        return (100, "Xu ly that bai")
    return mapping[status]


JsonDict = dict[str, Any]
