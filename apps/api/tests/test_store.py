from pathlib import Path

from media_agent_lab_api.models import JobStatus
from media_agent_lab_api.store import JobStore


def test_job_store_creates_and_reads_job(tmp_path: Path):
    store = JobStore(tmp_path / "app.db", tmp_path / "jobs")

    job = store.create_job("song.mp3")
    loaded = store.get_job(job.id)

    assert loaded.id == job.id
    assert loaded.status == JobStatus.UPLOADED
    assert loaded.original_filename == "song.mp3"
    assert (tmp_path / "jobs" / job.id / "input").is_dir()
    assert (tmp_path / "jobs" / job.id / "metadata").is_dir()


def test_job_store_updates_status(tmp_path: Path):
    store = JobStore(tmp_path / "app.db", tmp_path / "jobs")
    job = store.create_job("song.mp3")

    updated = store.update_status(job.id, JobStatus.GENERATING_PROMPT)

    assert updated.status == JobStatus.GENERATING_PROMPT
    assert updated.updated_at >= job.updated_at


def test_job_store_returns_none_for_missing_job(tmp_path: Path):
    store = JobStore(tmp_path / "app.db", tmp_path / "jobs")

    assert store.get_job("missing") is None
