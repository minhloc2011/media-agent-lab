import sqlite3
from pathlib import Path
from uuid import uuid4

from media_agent_lab_api.models import JobRecord, JobStatus, utc_now


class JobStore:
    def __init__(self, db_path: Path, jobs_root: Path):
        self.db_path = db_path
        self.jobs_root = jobs_root
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.jobs_root.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_code TEXT,
                    error_message TEXT
                )
                """
            )

    def create_job(self, original_filename: str) -> JobRecord:
        now = utc_now()
        record = JobRecord(
            id=str(uuid4()),
            status=JobStatus.UPLOADED,
            original_filename=original_filename,
            created_at=now,
            updated_at=now,
        )
        self.job_dir(record.id, create=True)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, status, original_filename, created_at, updated_at,
                    error_code, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.status.value,
                    record.original_filename,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                    record.error_code,
                    record.error_message,
                ),
            )
        return record

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        return JobRecord.model_validate(dict(row))

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> JobRecord:
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?, error_code = ?, error_message = ?
                WHERE id = ?
                """,
                (status.value, now.isoformat(), error_code, error_message, job_id),
            )
        record = self.get_job(job_id)
        if record is None:
            raise KeyError(f"Job not found: {job_id}")
        return record

    def job_dir(self, job_id: str, create: bool = False) -> Path:
        path = self.jobs_root / job_id
        if create:
            for child in ["input", "audio", "stems", "metadata", "logs"]:
                (path / child).mkdir(parents=True, exist_ok=True)
        return path

    def save_upload(self, job_id: str, filename: str, content: bytes) -> Path:
        suffix = Path(filename).suffix.lower() or ".mp3"
        path = self.job_dir(job_id, create=True) / "input" / f"original{suffix}"
        path.write_bytes(content)
        return path
