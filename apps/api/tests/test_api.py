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
