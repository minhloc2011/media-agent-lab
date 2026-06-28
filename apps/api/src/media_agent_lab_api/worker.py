import json

from media_agent_lab_api.models import AnalysisResult, JobStatus
from media_agent_lab_api.prompting import build_mock_analysis_result
from media_agent_lab_api.store import JobStore


PIPELINE_STATUSES = [
    JobStatus.VALIDATING,
    JobStatus.CONVERTING,
    JobStatus.SEPARATING_STEMS,
    JobStatus.ANALYZING_MIX,
    JobStatus.ANALYZING_VOCAL,
    JobStatus.DETECTING_LANGUAGE,
    JobStatus.GENERATING_PROMPT,
    JobStatus.COMPLETED,
]


def run_mock_pipeline(store: JobStore, job_id: str) -> AnalysisResult:
    for status in PIPELINE_STATUSES:
        store.update_status(job_id, status)

    result = build_mock_analysis_result()
    metadata_path = store.job_dir(job_id, create=True) / "metadata" / "result.json"
    metadata_path.write_text(
        json.dumps(result.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result
