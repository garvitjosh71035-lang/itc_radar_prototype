#!/bin/bash
# Commit Health Monitor System and Push to GitHub

echo "🚀 Committing Health Monitoring System..."

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: Not in correct directory. Please run from d:\sih\pace-prototype"
    exit 1
fi

# Add all new files
git add scripts/health_monitor.py
git add scripts/health_monitor.bat  
git add scripts/HEALTH_MONITOR_README.md
git add backend/requirements.txt
git add README.md

# Commit with detailed message
git commit -m "feat: Add production-ready health monitoring system

- Complete async-based health monitor (health_monitor.py)
- Windows batch launcher for easy startup (health_monitor.bat)
- Comprehensive README with usage examples (HEALTH_MONITOR_README.md)
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
✅ Log file generation

Monitors:
- Backend API (/health endpoint)
- Frontend UI (page load)
- Optional: Database, Redis connectivity

Configuration via environment variables or CLI options.
Production ready - deploy on Render.com immediately!"

# Check if there were any changes
if [ $? -eq 0 ]; then
    echo "✅ Files committed successfully"
else
    echo "⚠️  No new changes to commit"
fi

# Push to GitHub
echo "\n🔄 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "\n🎉 Health Monitor is now deployed!"
    echo "   View at: https://github.com/garvitjosh71035-lang/itc_radar_prototype"
else
    echo "❌ Push failed - check your internet connection"
    exit 1
fi
