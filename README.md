# Media Agent Lab

Local-first MVP for turning an MP3 reference track into a Vietnamese ACE-Step prompt.

## Target Local Runtime

- Windows workstation
- Python 3.12 venv at `.venv`
- NVIDIA GPU optional, validated with `scripts/check_cuda.ps1`
- FFmpeg provided by `imageio-ffmpeg` when system FFmpeg is unavailable
- Node.js and npm for the Vite web app

## First Slice

The current implementation is a CUDA-ready audio pipeline:

- FastAPI upload and job endpoints
- SQLite job store
- FFmpeg MP3-to-WAV conversion
- Demucs stem separation with CUDA when available
- librosa mix analysis
- deterministic ACE-Step prompt generation
- React upload/result UI
- local CUDA/FFmpeg smoke script

## Setup

If Python 3.12 is installed elsewhere, replace the hard-coded executable path with your local Python 3.12 path.

```powershell
C:\Users\ADMIN\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install --trusted-host download.pytorch.org --trusted-host download-r2.pytorch.org --trusted-host pypi.org --trusted-host files.pythonhosted.org torch==2.11.0+cu128 torchaudio==2.11.0+cu128 --index-url https://download.pytorch.org/whl/cu128 --extra-index-url https://pypi.org/simple
.\.venv\Scripts\python.exe -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .\apps\api[dev]
cd apps\web
npm.cmd install --strict-ssl=false
```

## Verify

```powershell
npm.cmd run api:test
npm.cmd run web:build
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

## Current Verification Status

The skeleton is considered healthy when these commands pass:

```powershell
npm.cmd run api:test
npm.cmd run web:build
npm.cmd run check:cuda
```

If `check:cuda` reports missing system FFmpeg but finds bundled `imageio-ffmpeg`, real audio conversion can still run. The first Demucs separation may take longer if model weights are not already cached locally.
