@echo off
REM PACE Health Monitor Launcher (Windows)
REM Quick startup script for health monitoring

echo Starting PACE Health Monitor...
echo Press Ctrl+C to stop

REM Check if running from correct directory
if not exist "backend\requirements.txt" (
    echo ERROR: Please run this script from d:\sih\pace-prototype directory
    pause
    exit /b 1
)

REM Run health monitor with default settings
python scripts/health_monitor.py --daemon

REM If we get here, monitor stopped
echo Health monitor stopped
pause
