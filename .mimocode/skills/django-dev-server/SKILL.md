---
name: django-dev-server
description: Start/restart Django dev server on Windows with correct PYTHONPATH for the env venv
---

# Django Dev Server (Windows)

The `env` venv has packages at `D:\Projects\katran\env\Lib\site-packages` but `.\env\Scripts\python.exe` doesn't include this in sys.path. Every manage.py command and the dev server require the PYTHONPATH workaround.

## Start/restart dev server

```powershell
# Kill any existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Set PYTHONPATH and start server
$pythonPath = "D:\Projects\katran\env\Scripts\python.exe"
$managePy = "D:\Projects\katran\manage.py"
$env:PYTHONPATH = "D:\Projects\katran\env\Lib\site-packages"
Start-Process -FilePath $pythonPath -ArgumentList "$managePy runserver"
```

## Run any manage.py command

```powershell
$env:PYTHONPATH = "D:\Projects\katran\env\Lib\site-packages"
& "D:\Projects\katran\env\Scripts\python.exe" "D:\Projects\katran\manage.py" <command>
```

## Verify server is running

```powershell
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000" -UseBasicParsing -TimeoutSec 5
    Write-Host "Server OK: $($response.StatusCode)"
} catch {
    Write-Host "Server not running or error: $_"
}
```

## Open site in browser

```powershell
Start-Process "http://127.0.0.1:8000"
```
