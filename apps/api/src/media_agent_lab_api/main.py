import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from media_agent_lab_api.config import database_path, jobs_dir
from media_agent_lab_api.models import (
    AnalysisResult,
    JobCreateResponse,
    JobStatusResponse,
    status_progress,
)
from media_agent_lab_api.pipeline import run_audio_pipeline
from media_agent_lab_api.store import JobStore


app = FastAPI(title="Media Agent Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_store() -> JobStore:
    return JobStore(database_path(), jobs_dir())


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job(
    file: UploadFile,
    store: JobStore = Depends(get_store),
) -> JobCreateResponse:
    filename = file.filename or "upload.mp3"
    if not filename.lower().endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only .mp3 uploads are supported")

    content = await file.read()
    job = store.create_job(filename)
    store.save_upload(job.id, filename, content)
    run_audio_pipeline(store, job.id)
    updated_job = store.get_job(job.id) or job
    return JobCreateResponse(job_id=updated_job.id, status=updated_job.status)


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    store: JobStore = Depends(get_store),
) -> JobStatusResponse:
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    progress, current_step = status_progress(job.status)
    return JobStatusResponse(
        id=job.id,
        status=job.status,
        progress=progress,
        current_step=current_step,
        error_code=job.error_code,
        error_message=job.error_message,
    )


@app.get("/api/jobs/{job_id}/result", response_model=AnalysisResult)
def get_job_result(
    job_id: str,
    store: JobStore = Depends(get_store),
) -> AnalysisResult:
    metadata_path = _metadata_path(store, job_id)
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    return AnalysisResult.model_validate(json.loads(metadata_path.read_text(encoding="utf-8")))


@app.get("/api/jobs/{job_id}/assets/{asset_name}")
def get_asset(
    job_id: str,
    asset_name: str,
    store: JobStore = Depends(get_store),
) -> FileResponse:
    if asset_name != "metadata":
        raise HTTPException(status_code=404, detail="Asset not available")
    metadata_path = _metadata_path(store, job_id)
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(metadata_path, media_type="application/json", filename="result.json")


def _metadata_path(store: JobStore, job_id: str) -> Path:
    return store.job_dir(job_id) / "metadata" / "result.json"
