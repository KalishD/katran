---
name: django-dev-server
description: Start/restart Django dev server on Windows with correct PYTHONPATH for the env venv
---

# Django Dev Server (Windows)

The `env` venv has packages at `C:\Users\KDGHome\katran\env\Lib\site-packages` but `.\env\Scripts\python.exe` doesn't include this in sys.path. Every manage.py command and the dev server require the PYTHONPATH workaround.

## Start/restart dev server

```powershell
# Kill any existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Set PYTHONPATH and start server
$env:PYTHONPATH = "C:\Users\KDGHome\katran\env\Lib\site-packages"
Start-Process -FilePath "D:\Projects\katran\env\Scripts\python.exe" -ArgumentList "manage.py runserver" -WorkingDirectory "D:\Projects\katran"
```

## Run any manage.py command

```powershell
$env:PYTHONPATH = "C:\Users\KDGHome\katran\env\Lib\site-packages"
.\env\Scripts\python.exe manage.py <command>
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
