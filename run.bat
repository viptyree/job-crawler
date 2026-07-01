@echo off
setlocal

REM ==================================================
REM Job Crawler one-click launcher
REM Project root:
REM F:\Codex job\kaifa\Goodjob
REM ==================================================

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"

set "BACKEND_URL=http://127.0.0.1:8000"
set "FRONTEND_URL=http://127.0.0.1:5173"

echo ============================================
echo Job Crawler Launcher
echo ============================================
echo ROOT: "%ROOT%"
echo BACKEND: "%BACKEND_DIR%"
echo FRONTEND: "%FRONTEND_DIR%"
echo.

if not exist "%BACKEND_DIR%\" (
  echo [ERROR] Backend directory not found:
  echo "%BACKEND_DIR%"
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\" (
  echo [ERROR] Frontend directory not found:
  echo "%FRONTEND_DIR%"
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js not found. Please install Node.js 18+ and add it to PATH.
  pause
  exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  set "PKG_MANAGER=npm"
  set "INSTALL_CMD=npm install"
  set "DEV_CMD=npm run dev -- --host 127.0.0.1 --port 5173"
) else (
  set "PKG_MANAGER=pnpm"
  set "INSTALL_CMD=pnpm install"
  set "DEV_CMD=pnpm dev --host 127.0.0.1 --port 5173"
)

echo Using package manager: %PKG_MANAGER%
echo.

echo Stopping old backend/frontend services on ports 8000 and 5173...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$targetIds=@(); $ports=@(8000,5173); foreach($port in $ports){ $targetIds += Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique }; $targetIds += Get-CimInstance Win32_Process | Where-Object { ($_.CommandLine -like '*uvicorn app.main:app*') -or ($_.CommandLine -like '*vite*--host*127.0.0.1*') -or ($_.CommandLine -like '*pnpm*dev*--host*127.0.0.1*') } | Select-Object -ExpandProperty ProcessId; $allIds=@($targetIds | Where-Object { $_ -and $_ -ne $PID } | Select-Object -Unique); $changed=$true; while($changed){ $children=Get-CimInstance Win32_Process | Where-Object { $allIds -contains $_.ParentProcessId } | Select-Object -ExpandProperty ProcessId; $newIds=@($children | Where-Object { $allIds -notcontains $_ }); $changed=$newIds.Count -gt 0; $allIds += $newIds }; $allIds | Sort-Object -Descending | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul
echo.

REM Start backend
start "job-crawler backend" cmd /k "cd /d ""%BACKEND_DIR%"" && python -c ""import uvicorn"" 2>nul && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload || (python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload)"

REM Start frontend
start "job-crawler frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && if not exist node_modules (%INSTALL_CMD% && %DEV_CMD%) else (%DEV_CMD%)"

echo Waiting for services to start...
timeout /t 8 /nobreak >nul

start "" "%FRONTEND_URL%"

echo.
echo Started.
echo Backend health: %BACKEND_URL%/health
echo Backend docs:   %BACKEND_URL%/docs
echo Frontend:       %FRONTEND_URL%
echo.
echo Keep the backend and frontend windows open while using the system.
pause
