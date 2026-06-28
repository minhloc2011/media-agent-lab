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
  Write-Warning "FFmpeg is not available on PATH. Checking bundled imageio-ffmpeg instead."
  $ffmpegCheck = @'
import imageio_ffmpeg
print(f'bundled_ffmpeg: {imageio_ffmpeg.get_ffmpeg_exe()}')
'@
  & $python -c $ffmpegCheck
}

Write-Host "Checking PyTorch CUDA..."
$torchCheck = @'
try:
    import torch
except ModuleNotFoundError:
    print('torch: missing')
    raise SystemExit(0)

print(f'torch: {torch.__version__}')
print(f'cuda_available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'cuda_device: {torch.cuda.get_device_name(0)}')
'@

& $python -c $torchCheck

Write-Host "Checking audio analysis packages..."
$audioCheck = @'
import librosa
import demucs
print(f'librosa: {librosa.__version__}')
print('demucs: installed')
'@

& $python -c $audioCheck

Write-Host "Environment smoke check finished."
