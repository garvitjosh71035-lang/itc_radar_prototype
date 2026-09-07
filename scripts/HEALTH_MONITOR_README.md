# 🔍 PACE Health Monitor - Production Monitoring System

## Overview

A comprehensive, production-ready health monitoring system that continuously checks your PACE prototype services (backend API, frontend UI, database) and provides real-time status updates, alerts, and statistics.

---

## ✨ Key Features

✅ **Automated Health Checks** - Every 5 minutes by default  
✅ **Uptime Tracking** - Calculates uptime percentages per service  
✅ **Performance Metrics** - Response time tracking (min/max/avg)  
✅ **Alert System** - Slack notifications on service failures  
✅ **Status Dashboard** - Beautiful terminal-based dashboard  
✅ **Graceful Shutdown** - Saves statistics before stopping  
✅ **Logging** - Comprehensive logging to files  
✅ **Statistics Export** - JSON export of all metrics  

---

## 🚀 Quick Start

### Option 1: Single Test Run

Test current service status with one check:

```bash
cd d:\sih\pace-prototype
python scripts/health_monitor.py
```

### Option 2: Continuous Monitoring (Production)

Run as background daemon, checking every 5 minutes:

```bash
# Windows
scripts/health_monitor.bat

# Or directly:
python scripts/health_monitor.py --daemon
```

### Option 3: Custom Settings

Monitor different URLs or adjust check frequency:

```bash
python scripts/health_monitor.py \
  --backend-url https://pace-backend.onrender.com \
  --frontend-url https://pace-frontend.onrender.com \
  --interval 180 \  # Check every 3 minutes
  --slack-webhook https://hooks.slack.com/services/YOUR_WEBHOOK_URL \
  --daemon
```

---

## ⚙️ Configuration

### Environment Variables

Set these in `.env` file or environment:

```bash
# Service URLs (defaults are localhost)
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Notification settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EMAIL_RECIPIENTS=admin@example.com,you@example.com
EMAIL_ENABLED=true

# Performance tuning
CHECK_INTERVAL=300  # Seconds between checks (default: 300 = 5 min)
```

### Command-Line Options

```bash
--daemon                Run continuously in background
--backend-url URL       Backend API URL (default: http://localhost:8000)
--frontend-url URL      Frontend UI URL (default: http://localhost:3000)
--interval SECONDS      Check interval in seconds (default: 300)
--slack-webhook URL     Slack webhook for alerts
```

---

## 📊 What It Monitors

### Services Tracked

| Service | Check Method | Endpoint |
|---------|-------------|----------|
| **Backend API** | HTTP GET + JSON validation | `/health` |
| **Frontend UI** | HTTP GET + page load | `/` |
| **Database** | Query test (optional) | PostgreSQL connection |
| **Redis Cache** | Connection test (optional) | Redis ping |

### Metrics Collected

- ✅ Response time (ms)
- ✅ Uptime percentage
- ✅ Total checks performed
- ✅ Consecutive failures
- ✅ Min/max response times
- ✅ Average response time

---

## 🎯 Usage Examples

### Local Development Testing

```bash
# Start your services first
docker-compose up -d

# Then run monitor
python scripts/health_monitor.py
```

Expected output:
```
2024-09-08 10:30:15 - INFO - Backend API: 45.23ms - healthy
2024-09-08 10:30:15 - INFO - Frontend UI: 123.45ms - healthy
...
🔍 PACE SYSTEM HEALTH DASHBOARD
================================================================================
Time: 2024-09-08 10:30:15
Uptime: 171015 seconds
--------------------------------------------------------------------------------

✅ Backend API
   URL: http://localhost:8000/health
   Status: HEALTHY
   Response Time: 45.23ms
   Total Checks: 1
   Uptime: 100.00%
```

### Render.com Production Deployment

After deploying to Render.com:

```bash
python scripts/health_monitor.py \
  --backend-url https://pace-backend.onrender.com \
  --frontend-url https://pace-frontend.onrender.com \
  --daemon
```

This will now continuously monitor your live production systems!

---

## 🔔 Alert System

### Slack Integration

Configure Slack webhook URL:

```bash
python scripts/health_monitor.py \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK"
```

**Alert triggers when:**
- Service down for 3+ consecutive checks (configurable)
- Response time exceeds 2 seconds (configurable)
- Database connection fails
- Redis cache unavailable

### Email Alerts (Optional)

Enable email notifications by setting `EMAIL_ENABLED=true` and `EMAIL_RECIPIENTS` in environment variables.

---

## 📁 Output Files

### Logs

Located in `logs/` directory:

**`health_monitor.log`**
- All health check events
- Errors and warnings
- Performance degradation notices
- Alert triggers

### Statistics

**`health_stats.json`** (auto-generated every 10 checks)

```json
{
  "timestamp": "2024-09-08T10:30:15",
  "running_duration": 3600,
  "services": {
    "backend": {
      "name": "Backend API",
      "status": "healthy",
      "uptime_percentage": 99.95,
      "average_response_time": 52.3
    },
    "frontend": {
      "name": "Frontend UI",
      "status": "healthy",
      "uptime_percentage": 100.0,
      "average_response_time": 125.7
    }
  }
}
```

---

## 🐛 Troubleshooting

### Issue: Monitor won't start

**Check:** Python version is 3.11+  
**Check:** aiohttp installed (`pip show aiohttp`)  
**Solution:** Reinstall dependencies (`pip install -r backend/requirements.txt`)

### Issue: Cannot connect to services

**Verify:** Services are running locally or accessible remotely  
**Check:** Firewall not blocking connections  
**Check:** SSL certificates valid (if using HTTPS)

### Issue: Too many alerts

**Adjust:** Increase `--interval` value to check less frequently  
**Adjust:** Increase `max_consecutive_failures` threshold

### Issue: High memory usage

**Solution:** Health monitor uses minimal RAM (~50-100MB). If higher, check for conflicts with other processes.

---

## 🎨 Dashboard Features

When running in daemon mode, you'll see:

```
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
   Min Response: 12.34ms
   Max Response: 892.45ms
   Avg Response: 48.67ms
   Uptime: 99.92%

✅ Frontend UI
   URL: http://localhost:3000
   Status: HEALTHY
   Response Time: 156.78ms
   Total Checks: 247
   Min Response: 89.12ms
   Max Response: 445.23ms
   Avg Response: 158.34ms
   Uptime: 100.00%

================================================================================
```

---

## 💡 Pro Tips

### Daily Summary Reports

Add cron job (Linux/Mac) or Task Scheduler (Windows):

```bash
# Linux cron - daily summary at 8 AM
0 8 * * * cd /path/to/pace && python scripts/health_monitor.py --summary
```

### Integration with CI/CD

In your deployment pipeline:

```yaml
# After deployment, run health check
deploy:
  steps:
    - name: Verify deployment
      run: |
        python scripts/health_monitor.py \
          --backend-url ${{ secrets.RENDER_BACKEND_URL }} \
          --daemon &
        sleep 60
```

### Load Testing Context

Use response time data to identify performance issues:

- **Response time > 2000ms** → Investigate database queries
- **Min vs Max variance high** → Memory leaks or resource contention
- **Uptime < 99%** → Review infrastructure stability

---

## 🔄 Updates & Maintenance

### Version 2.0 Changes

- ✅ Added async HTTP requests (faster, less resource-intensive)
- ✅ Improved alert system with Slack integration
- ✅ Better statistics calculation and export
- ✅ Graceful shutdown handling
- ✅ Comprehensive logging to files

### Future Enhancements

- [ ] Grafana/Prometheus integration
- [ ] Real-time web dashboard
- [ ] Advanced anomaly detection
- [ ] Multi-region monitoring
- [ ] Load testing automation

---

## 📞 Support

For issues or questions:
- Check log files in `logs/health_monitor.log`
- Review error messages in console output
- Verify network connectivity to monitored services
- Ensure all required dependencies installed

---

## 📄 License

Same license as main PACE project (MIT)

---

**Last Updated:** September 8, 2026  
**Version:** 2.0  
**Author:** PACE Team  
**Maintenance Status:** Active
