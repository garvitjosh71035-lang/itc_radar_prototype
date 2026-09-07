# 🔍 Quick Health Check Guide

## One-Command Health Test

### Windows (PowerShell)
```powershell
cd d:\sih\pace-prototype
python scripts/health_monitor.py
```

**What it does:** Runs one test check on all services and displays beautiful dashboard

---

## Continuous Monitoring (Production)

### Option 1: Windows Batch File (Easiest)
Double-click: `scripts\health_monitor.bat`

Or run in terminal:
```bash
scripts\health_monitor.bat
```

This runs continuously, checking every 5 minutes forever until you press Ctrl+C

### Option 2: Direct Command
```bash
python scripts/health_monitor.py --daemon
```

Same as above - monitors continuously in background

---

## Monitor Your Live Deployed System

After deploying to Render.com, monitor your LIVE production system:

```bash
python scripts/health_monitor.py \
  --backend-url https://pace-backend.onrender.com \
  --frontend-url https://pace-frontend.onrender.com \
  --interval 300 \
  --daemon
```

This will now watch your deployed services! 🚀

---

## What You'll See

When running the health monitor, you'll see output like:

```
✅ Backend API: 45.23ms - healthy
✅ Frontend UI: 123.45ms - healthy
================================================================================
🔍 PACE SYSTEM HEALTH DASHBOARD
================================================================================
Time: 2024-09-08 10:30:15
Uptime: 171015 seconds
--------------------------------------------------------------------------------

✅ Backend API
   URL: http://localhost:8000/health
   Status: HEALTHY
   Response Time: 45.23ms
   Total Checks: 247
   Consecutive Failures: 0
   Min Response: 12.34ms
   Max Response: 892.45ms
   Avg Response: 48.67ms
   Uptime: 99.92%

✅ Frontend UI
   URL: http://localhost:3000
   Status: HEALTHY
   Response Time: 156.78ms
   Total Checks: 247
   Consecutive Failures: 0
   Min Response: 89.12ms
   Max Response: 445.23ms
   Avg Response: 158.34ms
   Uptime: 100.00%

================================================================================
```

---

## Alert Configuration (Optional)

### Slack Alerts
Set up notifications when services go down:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
python scripts/health_monitor.py --daemon --slack-webhook $SLACK_WEBHOOK_URL
```

You'll get messages like:
```
🚨 ALERT: Backend API - Service down for 3 consecutive checks
```

---

## Files Created

When running, you'll notice:
- `logs/health_monitor.log` - All monitoring events logged here
- `health_stats.json` - Statistics exported in JSON format

---

## Stop Monitoring

Just press **Ctrl+C** in the terminal where it's running

The monitor will save current statistics before stopping gracefully.

---

## Troubleshooting

### Won't Start?
Check Python version (need 3.11+):
```powershell
python --version
```

### Can't Connect?
Verify your services are actually running:
```powershell
# Test backend
curl http://localhost:8000/health

# Test frontend  
curl http://localhost:3000
```

### Too Many Alerts?
Increase check interval:
```powershell
python scripts/health_monitor.py --interval 600  # Check every 10 minutes
```

---

## Production Deployment Tip

For continuous monitoring on Render.com:

1. Create a **Background Job** service
2. Point to same repository
3. Set command to: `python scripts/health_monitor.py --daemon`
4. This runs as a separate worker monitoring your main services

---

**That's it!** Your health monitor is ready to use! 🎉

For full documentation, see: `scripts/HEALTH_MONITOR_README.md`
