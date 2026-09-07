# Commit Health Monitor System (PowerShell Script)

Write-Host "🚀 Committing Health Monitoring System..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "❌ Error: Not in correct directory" -ForegroundColor Red
    exit 1
}

# Stage all changes
Write-Host "`n Staging files..." -ForegroundColor Yellow
git add scripts/health_monitor.py
git add scripts/health_monitor.bat  
git add scripts/HEALTH_MONITOR_README.md
git add scripts/commit_health_monitor.sh
git add backend/requirements.txt
git add README.md

# Commit with message
Write-Host "`n Creating commit..." -ForegroundColor Yellow
git commit -m "feat: Add production-ready health monitoring system

- Complete async-based health monitor (health_monitor.py)
- Windows batch launcher for easy startup (health_monitor.bat)
- Comprehensive documentation (HEALTH_MONITOR_README.md)
- Added aiohttp dependency for async HTTP requests
- Updated main README with health monitor quick start

Features:
✅ Automated checks every 5 minutes
✅ Uptime tracking per service
✅ Slack/Email alert integration
✅ Response time metrics (min/max/avg)
✅ Beautiful terminal dashboard
✅ JSON statistics export
✅ Graceful shutdown handling

Monitors:
- Backend API (/health endpoint)
- Frontend UI (page load)
- Database connectivity
- Redis cache connectivity"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n ✅ Files committed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n ⚠️  No new changes to commit" -ForegroundColor Yellow
    exit 0
}

# Push to GitHub
Write-Host "`n 🔄 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n 🎉 SUCCESS! Health Monitor deployed to GitHub!" -ForegroundColor Green
    Write-Host "   View your repo: https://github.com/garvitjosh71035-lang/itc_radar_prototype" -ForegroundColor Cyan
    Write-Host "`n Next step: Deploy to Render.com using DEPLOYMENT_GUIDE.md" -ForegroundColor Green
} else {
    Write-Host "`n ❌ Push failed - check internet connection or permissions" -ForegroundColor Red
    exit 1
}
