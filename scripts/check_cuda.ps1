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
    print('torch: missing')
    raise SystemExit(0)

print(f'torch: {torch.__version__}')
print(f'cuda_available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'cuda_device: {torch.cuda.get_device_name(0)}')
'@

& $python -c $torchCheck

Write-Host "Environment smoke check finished."
