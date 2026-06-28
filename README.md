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

If Python 3.12 is installed elsewhere, replace the hard-coded executable path with your local Python 3.12 path.

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

## Current Verification Status

The skeleton is considered healthy when these commands pass:

```powershell
npm.cmd run api:test
npm.cmd run web:build
npm.cmd run check:cuda
```

If `check:cuda` reports missing PyTorch or missing FFmpeg, the app skeleton can still run with the mock worker. Real audio processing should wait until those dependencies are installed and validated.
