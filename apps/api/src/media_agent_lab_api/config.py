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
