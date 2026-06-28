# CUDA-Ready MVP Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first runnable local MVP slice for Audio Intelligence Prompt Builder: CUDA environment checks, FastAPI job API, mock worker/result pipeline, and React upload/result UI.

**Architecture:** Create a small monorepo with `apps/api` for FastAPI/Python and `apps/web` for Vite/React. The backend persists jobs in SQLite and job folders under `data/jobs/<job_id>/`, while the first worker is deterministic and mockable so the UI and API can be verified before heavy audio dependencies are installed.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLite, pytest, Vite, React, TypeScript, Tailwind CSS, lucide-react, PowerShell smoke scripts, optional CUDA/PyTorch/Demucs checks.

---

## Scope

This plan implements Phase 0 and Phase 1 from the spec, plus a lightweight mock version of Phase 2. It does not install or run real FFmpeg conversion, librosa analysis, Demucs separation, or faster-whisper transcription. Instead it creates explicit service boundaries and smoke checks so those steps can be added in a later plan without reshaping the app.

## File Structure

- Create: `.gitignore` - ignores local envs, generated job files, node modules, build output, and caches.
- Create: `package.json` - root workspace commands for web and API convenience.
- Create: `apps/api/pyproject.toml` - Python package metadata and test configuration.
- Create: `apps/api/src/media_agent_lab_api/__init__.py` - package marker.
- Create: `apps/api/src/media_agent_lab_api/config.py` - resolves project paths and data directories.
- Create: `apps/api/src/media_agent_lab_api/models.py` - Pydantic models, job statuses, result schema.
- Create: `apps/api/src/media_agent_lab_api/store.py` - SQLite job persistence and filesystem paths.
- Create: `apps/api/src/media_agent_lab_api/prompting.py` - deterministic Vietnamese prompt generator for normalized mock metadata.
- Create: `apps/api/src/media_agent_lab_api/worker.py` - mock worker state transitions and result JSON writer.
- Create: `apps/api/src/media_agent_lab_api/main.py` - FastAPI routes.
- Create: `apps/api/tests/test_prompting.py` - unit tests for prompt mapping.
- Create: `apps/api/tests/test_store.py` - unit tests for job persistence.
- Create: `apps/api/tests/test_api.py` - API integration tests.
- Create: `scripts/check_cuda.ps1` - repeatable local environment smoke check.
- Create: `apps/web/package.json` - frontend dependencies and scripts.
- Create: `apps/web/index.html` - Vite entry HTML.
- Create: `apps/web/tsconfig.json` - TypeScript compiler configuration.
- Create: `apps/web/vite.config.ts` - Vite dev server and API proxy.
- Create: `apps/web/tailwind.config.ts` - Tailwind content config.
- Create: `apps/web/postcss.config.js` - Tailwind PostCSS config.
- Create: `apps/web/src/main.tsx` - React app entry.
- Create: `apps/web/src/App.tsx` - upload, polling, and result UI.
- Create: `apps/web/src/api.ts` - typed API client.
- Create: `apps/web/src/types.ts` - shared frontend response types.
- Create: `apps/web/src/index.css` - application styles.
- Create: `README.md` - local setup and run instructions.

## Task 1: Root Project Scaffolding

**Files:**
- Create: `.gitignore`
- Create: `package.json`
- Create: `README.md`

- [ ] **Step 1: Create root project metadata**

Create `.gitignore` with this content:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
*.pyc

node_modules/
dist/
.vite/

data/
coverage/
.env
.env.local
```

Create `package.json` with this content:

```json
{
  "name": "media-agent-lab",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "api:test": "cd apps/api && ..\\..\\.venv\\Scripts\\python.exe -m pytest",
    "api:dev": "cd apps/api && ..\\..\\.venv\\Scripts\\python.exe -m uvicorn media_agent_lab_api.main:app --reload --host 127.0.0.1 --port 8000",
    "web:dev": "cd apps/web && npm.cmd run dev",
    "web:build": "cd apps/web && npm.cmd run build",
    "check:cuda": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_cuda.ps1"
  }
}
```

Create `README.md` with this content:

````markdown
# Media Agent Lab

Local-first MVP for turning an MP3 reference track into a Vietnamese ACE-Step prompt.

## Target Local Runtime

- Windows workstation
- Python 3.12 venv at `.venv`
- NVIDIA GPU optional, validated with `scripts/check_cuda.ps1`
- FFmpeg required before real audio processing
- Node.js and npm for the Vite web app

## First Slice

The current implementation target is a CUDA-ready app skeleton:

- FastAPI upload and job endpoints
- SQLite job store
- deterministic mock worker result
- React upload/result UI
- local CUDA/FFmpeg smoke script

Real FFmpeg, librosa, Demucs, and faster-whisper integration come after this skeleton is stable.

## Setup

```powershell
C:\Users\ADMIN\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .\apps\api[dev]
cd apps\web
npm.cmd install
```

## Verify

```powershell
npm.cmd run api:test
npm.cmd run check:cuda
```

## Run

Terminal 1:

```powershell
npm.cmd run api:dev
```

Terminal 2:

```powershell
npm.cmd run web:dev
```
````

- [ ] **Step 2: Verify root metadata**

Run: `Get-Content package.json`

Expected: output includes `"api:test"`, `"api:dev"`, `"web:dev"`, and `"check:cuda"`.

- [ ] **Step 3: Commit**

```bash
git add .gitignore package.json README.md
git commit -m "chore: add root project scaffolding"
```

## Task 2: API Package And Core Models

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/media_agent_lab_api/__init__.py`
- Create: `apps/api/src/media_agent_lab_api/config.py`
- Create: `apps/api/src/media_agent_lab_api/models.py`
- Create: `apps/api/tests/test_prompting.py`

- [ ] **Step 1: Create Python package metadata**

Create `apps/api/pyproject.toml` with this content:

```toml
[project]
name = "media-agent-lab-api"
version = "0.1.0"
description = "FastAPI backend for Audio Intelligence Prompt Builder"
requires-python = ">=3.12,<3.13"
dependencies = [
  "fastapi>=0.115.0",
  "python-multipart>=0.0.9",
  "pydantic>=2.8.0",
  "uvicorn[standard]>=0.30.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "httpx>=0.27.0"
]

[build-system]
requires = ["setuptools>=70.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

Create `apps/api/src/media_agent_lab_api/__init__.py` with this content:

```python
"""Media Agent Lab API package."""
```

- [ ] **Step 2: Write failing prompt model test**

Create `apps/api/tests/test_prompting.py` with this content:

```python
from media_agent_lab_api.models import AnalysisResult, PromptResult, TrackAnalysis, VocalAnalysis


def test_analysis_result_serializes_prompt_contract():
    result = AnalysisResult(
        track=TrackAnalysis(
            bpm=82,
            tempo_bucket="cham",
            key="A",
            scale="minor",
            key_vi="La thu",
            energy="thap",
            brightness="sang",
            instrumentation=["piano chu dao", "trong nhe", "bass mem"],
            confidence={"bpm": 0.86, "key": 0.62, "instrumentation": 0.45},
        ),
        vocal=VocalAnalysis(
            median_pitch_hz=220.0,
            range_bucket="cao",
            voice_descriptor="giong cao sang",
            brightness="sang",
            power="nhe",
            confidence={"pitch": 0.78, "range": 0.7, "voice_descriptor": 0.55},
        ),
        prompt=PromptResult(
            tags_vi="nhac pop ballad Viet Nam, tempo cham 82 BPM",
            omitted_fields=["chords"],
            warnings=["genre la heuristic co confidence trung binh"],
        ),
    )

    payload = result.model_dump()

    assert payload["track"]["key_vi"] == "La thu"
    assert payload["vocal"]["voice_descriptor"] == "giong cao sang"
    assert payload["prompt"]["omitted_fields"] == ["chords"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_prompting.py -v`

Expected: FAIL with `ModuleNotFoundError` or import error for `media_agent_lab_api.models`.

- [ ] **Step 4: Implement config and models**

Create `apps/api/src/media_agent_lab_api/config.py` with this content:

```python
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def data_dir() -> Path:
    path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def jobs_dir() -> Path:
    path = data_dir() / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path() -> Path:
    return data_dir() / "app.db"
```

Create `apps/api/src/media_agent_lab_api/models.py` with this content:

```python
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


class VocalAnalysis(BaseModel):
    median_pitch_hz: float
    range_bucket: str
    voice_descriptor: str
    brightness: str
    power: str
    confidence: dict[str, float]


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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_prompting.py -v`

Expected: PASS for `test_analysis_result_serializes_prompt_contract`.

- [ ] **Step 6: Commit**

```bash
git add apps/api/pyproject.toml apps/api/src/media_agent_lab_api/__init__.py apps/api/src/media_agent_lab_api/config.py apps/api/src/media_agent_lab_api/models.py apps/api/tests/test_prompting.py
git commit -m "feat(api): add core models"
```

## Task 3: Prompt Generator

**Files:**
- Modify: `apps/api/tests/test_prompting.py`
- Create: `apps/api/src/media_agent_lab_api/prompting.py`

- [ ] **Step 1: Add failing prompt generator tests**

Append this content to `apps/api/tests/test_prompting.py`:

```python
from media_agent_lab_api.prompting import build_mock_analysis_result


def test_build_mock_analysis_result_includes_confident_fields():
    result = build_mock_analysis_result()

    assert result.prompt.tags_vi == (
        "nhac pop ballad Viet Nam, tempo cham 82 BPM, tong La thu, "
        "giong cao sang, am sac sang va tinh cam, piano chu dao, "
        "trong nhe, bass mem, khong khi cam xuc cho diep khuc tru tinh"
    )
    assert result.prompt.omitted_fields == ["chords"]
    assert "confidence trung binh" in result.prompt.warnings[0]


def test_build_mock_analysis_result_avoids_biometric_claims():
    result = build_mock_analysis_result()

    assert "nam" not in result.prompt.tags_vi.lower()
    assert "nu" not in result.prompt.tags_vi.lower()
    assert "ca si" not in result.prompt.tags_vi.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_prompting.py -v`

Expected: FAIL with `ModuleNotFoundError` or import error for `media_agent_lab_api.prompting`.

- [ ] **Step 3: Implement deterministic prompt generator**

Create `apps/api/src/media_agent_lab_api/prompting.py` with this content:

```python
from media_agent_lab_api.models import (
    AnalysisResult,
    LanguageAnalysis,
    PromptResult,
    TrackAnalysis,
    VocalAnalysis,
)


def build_mock_analysis_result() -> AnalysisResult:
    track = TrackAnalysis(
        bpm=82,
        tempo_bucket="cham",
        key="A",
        scale="minor",
        key_vi="La thu",
        energy="thap",
        brightness="sang",
        instrumentation=["piano chu dao", "trong nhe", "bass mem"],
        confidence={"bpm": 0.86, "key": 0.62, "instrumentation": 0.45},
    )
    vocal = VocalAnalysis(
        median_pitch_hz=220.0,
        range_bucket="cao",
        voice_descriptor="giong cao sang",
        brightness="sang",
        power="nhe",
        confidence={"pitch": 0.78, "range": 0.7, "voice_descriptor": 0.55},
    )
    language = LanguageAnalysis(
        detected="vi",
        label_vi="Viet Nam",
        confidence=0.74,
        used_in_prompt=True,
    )
    fragments = [
        "nhac pop ballad Viet Nam",
        f"tempo {track.tempo_bucket} {track.bpm} BPM",
        f"tong {track.key_vi}",
        vocal.voice_descriptor,
        "am sac sang va tinh cam",
        *track.instrumentation,
        "khong khi cam xuc cho diep khuc tru tinh",
    ]
    prompt = PromptResult(
        tags_vi=", ".join(fragments),
        omitted_fields=["chords"],
        warnings=["genre la heuristic co confidence trung binh"],
    )
    return AnalysisResult(track=track, vocal=vocal, language=language, prompt=prompt)
```

- [ ] **Step 4: Run prompt tests**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_prompting.py -v`

Expected: all tests in `test_prompting.py` PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/media_agent_lab_api/prompting.py apps/api/tests/test_prompting.py
git commit -m "feat(api): add mock prompt generator"
```

## Task 4: SQLite Job Store

**Files:**
- Create: `apps/api/src/media_agent_lab_api/store.py`
- Create: `apps/api/tests/test_store.py`

- [ ] **Step 1: Write failing store tests**

Create `apps/api/tests/test_store.py` with this content:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_store.py -v`

Expected: FAIL with import error for `media_agent_lab_api.store`.

- [ ] **Step 3: Implement store**

Create `apps/api/src/media_agent_lab_api/store.py` with this content:

```python
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
```

- [ ] **Step 4: Run store tests**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_store.py -v`

Expected: all tests in `test_store.py` PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/media_agent_lab_api/store.py apps/api/tests/test_store.py
git commit -m "feat(api): add sqlite job store"
```

## Task 5: Mock Worker And FastAPI Routes

**Files:**
- Create: `apps/api/src/media_agent_lab_api/worker.py`
- Create: `apps/api/src/media_agent_lab_api/main.py`
- Create: `apps/api/tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

Create `apps/api/tests/test_api.py` with this content:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from media_agent_lab_api import main
from media_agent_lab_api.store import JobStore


def make_client(tmp_path: Path) -> TestClient:
    main.app.dependency_overrides[main.get_store] = lambda: JobStore(
        tmp_path / "app.db",
        tmp_path / "jobs",
    )
    return TestClient(main.app)


def test_health_endpoint_reports_ok(tmp_path: Path):
    client = make_client(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_rejects_non_mp3(tmp_path: Path):
    client = make_client(tmp_path)

    response = client.post(
        "/api/jobs",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only .mp3 uploads are supported"


def test_create_job_runs_mock_pipeline(tmp_path: Path):
    client = make_client(tmp_path)

    create_response = client.post(
        "/api/jobs",
        files={"file": ("song.mp3", b"fake-mp3-bytes", "audio/mpeg")},
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/jobs/{job_id}")
    result_response = client.get(f"/api/jobs/{job_id}/result")

    assert create_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["progress"] == 100
    assert "nhac pop ballad Viet Nam" in result_response.json()["prompt"]["tags_vi"]


def test_metadata_asset_returns_result_json(tmp_path: Path):
    client = make_client(tmp_path)
    create_response = client.post(
        "/api/jobs",
        files={"file": ("song.mp3", b"fake-mp3-bytes", "audio/mpeg")},
    )
    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}/assets/metadata")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_api.py -v`

Expected: FAIL with import error for `media_agent_lab_api.main`.

- [ ] **Step 3: Implement mock worker**

Create `apps/api/src/media_agent_lab_api/worker.py` with this content:

```python
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
```

- [ ] **Step 4: Implement FastAPI routes**

Create `apps/api/src/media_agent_lab_api/main.py` with this content:

```python
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
from media_agent_lab_api.store import JobStore
from media_agent_lab_api.worker import run_mock_pipeline


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
    run_mock_pipeline(store, job.id)
    return JobCreateResponse(job_id=job.id, status=job.status)


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
        raise HTTPException(status_code=404, detail="Asset not available in mock pipeline")
    metadata_path = _metadata_path(store, job_id)
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(metadata_path, media_type="application/json", filename="result.json")


def _metadata_path(store: JobStore, job_id: str) -> Path:
    return store.job_dir(job_id) / "metadata" / "result.json"
```

- [ ] **Step 5: Run API tests**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest tests/test_api.py -v`

Expected: all tests in `test_api.py` PASS.

- [ ] **Step 6: Run full API test suite**

Run: `cd apps/api && ..\..\.venv\Scripts\python.exe -m pytest -v`

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/api/src/media_agent_lab_api/worker.py apps/api/src/media_agent_lab_api/main.py apps/api/tests/test_api.py
git commit -m "feat(api): add mock job pipeline"
```

## Task 6: Local Environment Smoke Script

**Files:**
- Create: `scripts/check_cuda.ps1`

- [ ] **Step 1: Create smoke check script**

Create `scripts/check_cuda.ps1` with this content:

```powershell
$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  $python = "C:\Users\ADMIN\AppData\Local\Programs\Python\Python312\python.exe"
}

Write-Host "Checking NVIDIA driver..."
nvidia-smi

Write-Host "Checking Python runtime..."
& $python --version

Write-Host "Checking FFmpeg..."
try {
  ffmpeg -version | Select-Object -First 1
} catch {
  Write-Warning "FFmpeg is not available on PATH. Real audio conversion will not work yet."
}

Write-Host "Checking PyTorch CUDA..."
$torchCheck = @'
try:
    import torch
except ModuleNotFoundError:
    print("torch: missing")
    raise SystemExit(0)

print(f"torch: {torch.__version__}")
print(f"cuda_available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"cuda_device: {torch.cuda.get_device_name(0)}")
'@

& $python -c $torchCheck

Write-Host "Environment smoke check finished."
```

- [ ] **Step 2: Run smoke script**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_cuda.ps1`

Expected: command prints `NVIDIA-SMI`, Python 3.12 version, an FFmpeg warning if FFmpeg is not installed, and either `torch: missing` or CUDA availability details.

- [ ] **Step 3: Commit**

```bash
git add scripts/check_cuda.ps1
git commit -m "chore: add cuda smoke check"
```

## Task 7: Web App Skeleton And API Client

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/index.html`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/vite.config.ts`
- Create: `apps/web/tailwind.config.ts`
- Create: `apps/web/postcss.config.js`
- Create: `apps/web/src/types.ts`
- Create: `apps/web/src/api.ts`
- Create: `apps/web/src/main.tsx`
- Create: `apps/web/src/App.tsx`
- Create: `apps/web/src/index.css`

- [ ] **Step 1: Create web package config**

Create `apps/web/package.json` with this content:

```json
{
  "name": "media-agent-lab-web",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1 --port 5173",
    "build": "tsc && vite build",
    "preview": "vite preview --host 127.0.0.1 --port 4173"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.4.0",
    "typescript": "^5.5.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.468.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  },
  "devDependencies": {}
}
```

Create `apps/web/index.html` with this content:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Media Agent Lab</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `apps/web/tsconfig.json` with this content:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": []
}
```

Create `apps/web/vite.config.ts` with this content:

```typescript
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000"
    }
  }
});
```

Create `apps/web/tailwind.config.ts` with this content:

```typescript
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {}
  },
  plugins: []
} satisfies Config;
```

Create `apps/web/postcss.config.js` with this content:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};
```

- [ ] **Step 2: Create typed API client**

Create `apps/web/src/types.ts` with this content:

```typescript
export type JobStatus =
  | "uploaded"
  | "validating"
  | "converting"
  | "separating_stems"
  | "analyzing_mix"
  | "analyzing_vocal"
  | "detecting_language"
  | "generating_prompt"
  | "completed"
  | "failed_validation"
  | "failed_convert"
  | "failed_demucs"
  | "failed_mix_analysis"
  | "failed_vocal_analysis"
  | "failed_language_detection"
  | "failed_prompt_generation";

export interface JobCreateResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  id: string;
  status: JobStatus;
  progress: number;
  current_step: string;
  error_code: string | null;
  error_message: string | null;
}

export interface AnalysisResult {
  track: {
    bpm: number;
    tempo_bucket: string;
    key: string;
    scale: string;
    key_vi: string;
    energy: string;
    brightness: string;
    instrumentation: string[];
    confidence: Record<string, number>;
  };
  vocal: {
    median_pitch_hz: number;
    range_bucket: string;
    voice_descriptor: string;
    brightness: string;
    power: string;
    confidence: Record<string, number>;
  };
  language: {
    detected: string | null;
    label_vi: string | null;
    confidence: number;
    used_in_prompt: boolean;
  };
  prompt: {
    tags_vi: string;
    omitted_fields: string[];
    warnings: string[];
  };
}
```

Create `apps/web/src/api.ts` with this content:

```typescript
import type { AnalysisResult, JobCreateResponse, JobStatusResponse } from "./types";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createJob(file: File): Promise<JobCreateResponse> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch("/api/jobs", {
    method: "POST",
    body: form
  });
  return parseJson<JobCreateResponse>(response);
}

export async function getJob(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`/api/jobs/${jobId}`);
  return parseJson<JobStatusResponse>(response);
}

export async function getResult(jobId: string): Promise<AnalysisResult> {
  const response = await fetch(`/api/jobs/${jobId}/result`);
  return parseJson<AnalysisResult>(response);
}
```

- [ ] **Step 3: Create React UI**

Create `apps/web/src/main.tsx` with this content:

```typescript
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Create `apps/web/src/App.tsx` with this content:

```typescript
import { Clipboard, Download, FileAudio, Loader2, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { createJob, getJob, getResult } from "./api";
import type { AnalysisResult, JobStatusResponse } from "./types";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<JobStatusResponse | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const canUpload = useMemo(() => file !== null && !isUploading, [file, isUploading]);

  useEffect(() => {
    if (!jobId || job?.status === "completed") {
      return;
    }

    const timer = window.setInterval(async () => {
      const nextJob = await getJob(jobId);
      setJob(nextJob);
      if (nextJob.status === "completed") {
        setResult(await getResult(jobId));
      }
    }, 1000);

    return () => window.clearInterval(timer);
  }, [jobId, job?.status]);

  async function handleUpload() {
    if (!file) {
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const created = await createJob(file);
      setJobId(created.job_id);
      const current = await getJob(created.job_id);
      setJob(current);
      if (current.status === "completed") {
        setResult(await getResult(created.job_id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function copyPrompt() {
    if (result) {
      await navigator.clipboard.writeText(result.prompt.tags_vi);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-5 py-8">
        <header className="flex items-center justify-between border-b border-neutral-800 pb-5">
          <div>
            <h1 className="text-2xl font-semibold">Media Agent Lab</h1>
            <p className="mt-1 text-sm text-neutral-400">MP3 reference to Vietnamese ACE-Step prompt</p>
          </div>
          <div className="rounded bg-emerald-500/15 px-3 py-1 text-sm text-emerald-300">CUDA-ready MVP</div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
          <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
            <div className="flex items-center gap-3">
              <FileAudio className="h-5 w-5 text-cyan-300" />
              <h2 className="text-lg font-medium">Upload MP3</h2>
            </div>
            <label className="mt-5 flex min-h-48 cursor-pointer flex-col items-center justify-center rounded border border-dashed border-neutral-700 bg-neutral-950 px-4 text-center hover:border-cyan-400">
              <Upload className="mb-3 h-8 w-8 text-neutral-500" />
              <span className="text-sm text-neutral-300">{file ? file.name : "Choose one .mp3 file"}</span>
              <input
                className="hidden"
                type="file"
                accept=".mp3,audio/mpeg"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <button
              className="mt-4 flex w-full items-center justify-center gap-2 rounded bg-cyan-400 px-4 py-2 font-medium text-neutral-950 disabled:cursor-not-allowed disabled:bg-neutral-700 disabled:text-neutral-400"
              disabled={!canUpload}
              onClick={handleUpload}
            >
              {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              Analyze
            </button>
            {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
          </div>

          <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="text-lg font-medium">Job Status</h2>
            {job ? (
              <div className="mt-5">
                <div className="flex items-center justify-between text-sm text-neutral-300">
                  <span>{job.current_step}</span>
                  <span>{job.progress}%</span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded bg-neutral-800">
                  <div className="h-full bg-cyan-400" style={{ width: `${job.progress}%` }} />
                </div>
                <p className="mt-3 text-xs text-neutral-500">{job.id}</p>
              </div>
            ) : (
              <p className="mt-5 text-sm text-neutral-400">Upload a file to create a local analysis job.</p>
            )}
          </div>
        </section>

        {result && (
          <section className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
            <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
              <div className="flex items-center justify-between gap-4">
                <h2 className="text-lg font-medium">ACE-Step Prompt</h2>
                <button className="rounded bg-neutral-100 px-3 py-2 text-sm font-medium text-neutral-950" onClick={copyPrompt}>
                  <Clipboard className="mr-2 inline h-4 w-4" />
                  Copy
                </button>
              </div>
              <p className="mt-5 text-xl leading-relaxed text-neutral-100">{result.prompt.tags_vi}</p>
              <a
                className="mt-5 inline-flex items-center gap-2 text-sm text-cyan-300"
                href={`/api/jobs/${jobId}/assets/metadata`}
              >
                <Download className="h-4 w-4" />
                Download metadata JSON
              </a>
            </div>

            <div className="rounded border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-lg font-medium">Metadata</h2>
              <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <dt className="text-neutral-500">Tempo</dt>
                <dd>{result.track.bpm} BPM</dd>
                <dt className="text-neutral-500">Key</dt>
                <dd>{result.track.key_vi}</dd>
                <dt className="text-neutral-500">Voice</dt>
                <dd>{result.vocal.voice_descriptor}</dd>
                <dt className="text-neutral-500">Brightness</dt>
                <dd>{result.track.brightness}</dd>
              </dl>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
```

Create `apps/web/src/index.css` with this content:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html {
  background: #0a0a0a;
}

body {
  margin: 0;
  min-width: 320px;
}

button,
input {
  font: inherit;
}
```

- [ ] **Step 4: Install web dependencies**

Run: `cd apps/web && npm.cmd install`

Expected: npm installs dependencies and creates `apps/web/package-lock.json`.

- [ ] **Step 5: Build web app**

Run: `cd apps/web && npm.cmd run build`

Expected: TypeScript and Vite build PASS and create `apps/web/dist`.

- [ ] **Step 6: Commit**

```bash
git add apps/web/package.json apps/web/package-lock.json apps/web/index.html apps/web/tsconfig.json apps/web/vite.config.ts apps/web/tailwind.config.ts apps/web/postcss.config.js apps/web/src
git commit -m "feat(web): add upload result ui"
```

## Task 8: End-To-End Local Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run API tests**

Run: `npm.cmd run api:test`

Expected: pytest reports all tests PASS.

- [ ] **Step 2: Run CUDA smoke check**

Run: `npm.cmd run check:cuda`

Expected: `nvidia-smi` prints the RTX 4060, Python prints version 3.12, FFmpeg warning appears if FFmpeg is missing, and PyTorch reports either missing or CUDA visibility.

- [ ] **Step 3: Run web build**

Run: `npm.cmd run web:build`

Expected: Vite build PASS.

- [ ] **Step 4: Update README verification notes**

Append this content to `README.md`:

````markdown
## Current Verification Status

The skeleton is considered healthy when these commands pass:

```powershell
npm.cmd run api:test
npm.cmd run web:build
npm.cmd run check:cuda
```

If `check:cuda` reports missing PyTorch or missing FFmpeg, the app skeleton can still run with the mock worker. Real audio processing should wait until those dependencies are installed and validated.
````

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add verification status"
```

## Self-Review

Spec coverage:

- Upload one MP3: Task 5 and Task 7 create the route and UI.
- Job progress and result page: Task 5 provides status/result endpoints; Task 7 renders progress and prompt.
- Metadata JSON download: Task 5 exposes `metadata` asset; Task 7 links to it.
- SQLite and local job folders: Task 4 implements `data/app.db` and `data/jobs/<job_id>/`.
- CUDA bootstrap: Task 6 implements repeatable environment checks.
- Prompt policy: Task 3 avoids identity and real-gender claims in the generated mock prompt.
- Real FFmpeg/Demucs/librosa/faster-whisper: intentionally deferred to the next implementation plan after this skeleton passes.

Placeholder scan:

- No placeholder markers.
- No undefined file paths.
- No tasks that say to add tests without exact test code.
- No implementation step that introduces a function without showing the function body.

Type consistency:

- Backend `JobStatus` string values match frontend `JobStatus` union values.
- `AnalysisResult` response shape matches the frontend `AnalysisResult` interface.
- API route names match frontend client calls.
