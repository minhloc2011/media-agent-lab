import json
from pathlib import Path
from typing import Protocol

from media_agent_lab_api.audio_converter import AudioConverter
from media_agent_lab_api.mix_analyzer import analyze_mix
from media_agent_lab_api.models import AnalysisResult, JobStatus, TrackAnalysis
from media_agent_lab_api.prompting import build_analysis_result
from media_agent_lab_api.stem_separator import DemucsStemSeparator, StemPaths
from media_agent_lab_api.store import JobStore


class Converter(Protocol):
    def convert_to_wav(self, source: Path, target: Path) -> Path: ...


class Separator(Protocol):
    def separate(self, wav_path: Path, stems_dir: Path, work_dir: Path) -> StemPaths: ...


class AudioPipeline:
    def __init__(
        self,
        converter: Converter | None = None,
        separator: Separator | None = None,
        mix_analyzer=analyze_mix,
    ):
        self.converter = converter or AudioConverter()
        self.separator = separator or DemucsStemSeparator()
        self.mix_analyzer = mix_analyzer

    def run(self, store: JobStore, job_id: str) -> AnalysisResult:
        job = store.get_job(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")

        try:
            store.update_status(job_id, JobStatus.CONVERTING)
            job_dir = store.job_dir(job_id, create=True)
            original = _find_original(job_dir)
            wav_path = self.converter.convert_to_wav(original, job_dir / "audio" / "input.wav")

            store.update_status(job_id, JobStatus.SEPARATING_STEMS)
            stems = self.separator.separate(wav_path, job_dir / "stems", job_dir / "demucs")

            store.update_status(job_id, JobStatus.ANALYZING_MIX)
            track = self.mix_analyzer(wav_path)
            instrumentation = list(track.instrumentation)
            if stems.vocals.exists():
                instrumentation.append("vocals da tach")
            if stems.drums.exists():
                instrumentation.append("trong da tach")
            track = track.model_copy(update={"instrumentation": instrumentation})

            store.update_status(job_id, JobStatus.GENERATING_PROMPT)
            result = build_analysis_result(track)
            metadata_path = job_dir / "metadata" / "result.json"
            metadata_path.write_text(
                json.dumps(result.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            store.update_status(job_id, JobStatus.COMPLETED)
            return result
        except Exception as exc:
            store.update_status(job_id, JobStatus.FAILED_PROMPT_GENERATION, "pipeline_error", str(exc))
            raise


def run_audio_pipeline(store: JobStore, job_id: str) -> AnalysisResult:
    return AudioPipeline().run(store, job_id)


def _find_original(job_dir: Path) -> Path:
    input_dir = job_dir / "input"
    candidates = sorted(input_dir.glob("original.*"))
    if not candidates:
        raise FileNotFoundError(f"No uploaded original file found in {input_dir}")
    return candidates[0]
