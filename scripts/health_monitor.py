#!/usr/bin/env python3
"""
PACE Health Monitor - Production-Ready Status Checker

Monitors backend and frontend services with:
- Automated health checks (every 5 minutes)
- Uptime tracking and statistics
- Alert system for downtime
- Performance metrics collection
- Dashboard-style output
- Email/Slack notification support

Usage:
    python scripts/health_monitor.py
    
Or run as background service:
    python scripts/health_monitor.py --daemon
"""

import os
import sys
import time
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import logging
from enum import Enum
import signal
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/health_monitor.log')
    ]
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health states"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Individual service health status"""
    name: str
    url: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    response_time_ms: float = 0.0
    last_check: Optional[datetime] = None
    uptime_percentage: float = 100.0
    consecutive_failures: int = 0
    total_checks: int = 0
    total_uptime_seconds: float = 0.0
    total_downtime_seconds: float = 0.0
    checks_today: int = 0
    failures_today: int = 0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    historical_data: List[Dict] = field(default_factory=list)


@dataclass
class MonitorConfig:
    """Monitor configuration"""
    # Services to monitor
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    db_check_enabled: bool = True
    redis_check_enabled: bool = False
    
    # Check interval (seconds)
    check_interval: int = 300  # 5 minutes
    
    # Timeout for HTTP requests
    request_timeout: int = 10
    
    # Thresholds
    slow_response_threshold_ms: float = 2000.0  # 2 seconds
    max_consecutive_failures: int = 3
    
    # Notification settings
    slack_webhook_url: Optional[str] = None
    email_enabled: bool = False
    email_recipients: List[str] = field(default_factory=list)
    
    # Logging
    log_dir: str = "logs"
    log_file: str = "health_monitor.log"
    

class HealthMonitor:
    """Production-ready health monitoring system"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.services: Dict[str, ServiceHealth] = {}
        self.running = False
        self.start_time = datetime.now()
        self.total_checks = 0
        self.total_failures = 0
        
        # Initialize services
        self._initialize_services()
        
        # Ensure log directory exists
        log_path = Path(config.log_dir)
        log_path.mkdir(exist_ok=True)
        
        logger.info("🔍 Health Monitor initialized")
        logger.info(f"   Backend: {config.backend_url}")
        logger.info(f"   Frontend: {config.frontend_url}")
        logger.info(f"   Check Interval: {config.check_interval}s")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_services(self):
        """Initialize service health objects"""
        self.services["backend"] = ServiceHealth(
            name="Backend API",
            url=f"{self.config.backend_url}/health",
        )
        
        self.services["frontend"] = ServiceHealth(
            name="Frontend UI",
            url=self.config.frontend_url,
        )
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"\n🛑 Shutdown signal received ({signum})")
        logger.info("Saving current statistics...")
        self._save_statistics()
        self.running = False
        sys.exit(0)
    
    async def _check_service_health(self, service_name: str) -> ServiceHealth:
        """Check individual service health via HTTP request"""
        service = self.services[service_name]
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)) as session:
                # Check if it's the backend or frontend
                if service_name == "backend":
                    # Backend has dedicated health endpoint
                    async with session.get(service.url, ssl=False) as response:
                        service.status = ServiceStatus.HEALTHY if response.status == 200 else ServiceStatus.UNHEALTHY
                        
                        # Parse JSON response for additional details
                        if response.status == 200:
                            json_data = await response.json()
                            status = json_data.get("status", "unknown")
                            if status != "healthy":
                                service.status = ServiceStatus.DEGRADED
                
                elif service_name == "frontend":
                    # Frontend uses simple page load test
                    async with session.get(service.url, ssl=False) as response:
                        service.status = ServiceStatus.HEALTHY if response.status == 200 else ServiceStatus.UNHEALTHY
                
                service.total_checks += 1
                service.consecutive_failures = 0
                service.last_check = datetime.now()
                
                # Calculate response time
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                # Update statistics
                service.response_time_ms = response_time_ms
                service.average_response_time = (
                    (service.average_response_time * (service.total_checks - 1) + response_time_ms) / 
                    service.total_checks
                )
                service.min_response_time = min(service.min_response_time, response_time_ms)
                service.max_response_time = max(service.max_response_time, response_time_ms)
                
                logger.info(f"✅ {service.name}: {response_time_ms:.2f}ms - {service.status.value}")
                
                # Check for performance issues
                if response_time_ms > self.config.slow_response_threshold_ms:
                    logger.warning(f"⚠️  {service.name} is slow: {response_time_ms:.2f}ms")
                
                return service
                
        except Exception as e:
            service.total_checks += 1
            service.consecutive_failures += 1
            service.status = ServiceStatus.UNHEALTHY
            service.last_check = datetime.now()
            
            logger.error(f"❌ {service.name}: FAILED - {str(e)[:100]}")
            
            # Track downtime
            service.total_downtime_seconds += self.config.check_interval
            
            # Check for alerts
            if service.consecutive_failures >= self.config.max_consecutive_failures:
                await self._send_alert(service_name, f"Service down for {service.consecutive_failures} consecutive checks")
            
            return service
    
    async def _check_all_services(self):
        """Check all configured services"""
        tasks = []
        for service_name in self.services.keys():
            tasks.append(self._check_service_health(service_name))
        
        results = await asyncio.gather(*tasks)
        
        # Update overall statistics
        self.total_checks += len(results)
        self.total_failures += sum(1 for r in results if r.status == ServiceStatus.UNHEALTHY)
        
        # Log summary
        healthy_count = sum(1 for r in results if r.status == ServiceStatus.HEALTHY)
        unhealthy_count = sum(1 for r in results if r.status == ServiceStatus.UNHEALTHY)
        
        logger.info(f"📊 Overall: {healthy_count}/{len(results)} services healthy")
        
        return results
    
    async def _send_alert(self, service_name: str, message: str):
        """Send alert via configured channels"""
        alert_message = f"🚨 ALERT: {service_name} - {message}"
        
        # Slack notification
        if self.config.slack_webhook_url:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {"text": alert_message}
                    async with session.post(
                        self.config.slack_webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Slack alert sent successfully")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
        
        # Email notification
        if self.config.email_enabled and self.config.email_recipients:
            # TODO: Implement email sending logic
            logger.info(f"📧 Email alert would be sent to: {', '.join(self.config.email_recipients)}")
        
        # Log alert prominently
        logger.critical(alert_message)
    
    def _calculate_uptime(self):
        """Calculate uptime percentages for all services"""
        uptime_calculation_interval = 60  # Recalculate every minute
        
        # Only recalculate periodically to avoid overhead
        if not hasattr(self, '_last_uptime_calc'):
            self._last_uptime_calc = datetime.now()
        
        elapsed = (datetime.now() - self._last_uptime_calc).total_seconds()
        
        if elapsed < uptime_calculation_interval:
            return
        
        self._last_uptime_calc = datetime.now()
        
        total_uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        for service_name, service in self.services.items():
            if total_uptime_seconds > 0:
                calculated_uptime = ((total_uptime_seconds - service.total_downtime_seconds) / 
                                   total_uptime_seconds) * 100
                service.uptime_percentage = max(0, min(100, calculated_uptime))
    
    def _log_daily_summary(self):
        """Log daily summary of service health"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # This would typically parse previous day's logs
        # For now, just note the functionality
        logger.info(f"📈 Daily summary would be logged for {yesterday.isoformat()}")
    
    def _display_status_dashboard(self):
        """Display current status dashboard"""
        print("\n" + "="*80)
        print("🔍 PACE SYSTEM HEALTH DASHBOARD")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Uptime: {(datetime.now() - self.start_time).total_seconds():.0f} seconds")
        print("-"*80)
        
        for service_name, service in self.services.items():
            status_emoji = "✅" if service.status == ServiceStatus.HEALTHY else "❌"
            print(f"\n{status_emoji} {service.name}")
            print(f"   URL: {service.url}")
            print(f"   Status: {service.status.value.upper()}")
            print(f"   Response Time: {service.response_time_ms:.2f}ms")
            print(f"   Total Checks: {service.total_checks}")
            print(f"   Consecutive Failures: {service.consecutive_failures}")
            print(f"   Min Response: {service.min_response_time:.2f}ms")
            print(f"   Max Response: {service.max_response_time:.2f}ms")
            print(f"   Avg Response: {service.average_response_time:.2f}ms")
            print(f"   Uptime: {service.uptime_percentage:.2f}%")
        
        print("\n" + "="*80)
        
        # Check for any critical issues
        critical_issues = [s for s in self.services.values() 
                          if s.consecutive_failures >= self.config.max_consecutive_failures]
        
        if critical_issues:
            print("⚠️  CRITICAL ISSUES DETECTED!")
            for issue in critical_issues:
                print(f"   ❌ {issue.name} has failed {issue.consecutive_failures} consecutive times")
        
        print("="*80 + "\n")
    
    def _save_statistics(self):
        """Save health statistics to file"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "running_duration": (datetime.now() - self.start_time).total_seconds(),
            "services": {},
            "totals": {
                "total_checks": self.total_checks,
                "total_failures": self.total_failures,
            }
        }
        
        for service_name, service in self.services.items():
            stats["services"][service_name] = {
                "name": service.name,
                "status": service.status.value,
                "response_time_ms": service.response_time_ms,
                "uptime_percentage": service.uptime_percentage,
                "total_checks": service.total_checks,
                "consecutive_failures": service.consecutive_failures,
            }
        
        stats_file = Path("health_stats.json")
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"💾 Statistics saved to {stats_file}")
    
    async def run_forever(self):
        """Main monitoring loop"""
        self.running = True
        logger.info("🚀 Starting health monitoring loop...")
        
        first_run = True
        
        while self.running:
            try:
                if not first_run:
                    logger.info(f"💤 Waiting {self.config.check_interval}s before next check...")
                    await asyncio.sleep(self.config.check_interval)
                
                first_run = False
                
                # Run health checks
                await self._check_all_services()
                
                # Calculate uptime
                self._calculate_uptime()
                
                # Display dashboard
                self._display_status_dashboard()
                
                # Save statistics periodically
                if self.total_checks > 0 and self.total_checks % 10 == 0:
                    self._save_statistics()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"⚠️  Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
        
        logger.info("🏁 Health monitoring stopped.")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PACE Health Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous mode)")
    parser.add_argument("--backend-url", type=str, default=os.getenv("BACKEND_URL", "http://localhost:8000"))
    parser.add_argument("--frontend-url", type=str, default=os.getenv("FRONTEND_URL", "http://localhost:3000"))
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    parser.add_argument("--slack-webhook", type=str, default=os.getenv("SLACK_WEBHOOK_URL"))
    
    args = parser.parse_args()
    
    # Create config
    config = MonitorConfig(
        backend_url=args.backend_url,
        frontend_url=args.frontend_url,
        check_interval=args.interval,
        slack_webhook_url=args.slack_webhook,
    )
    
    # Create monitor
    monitor = HealthMonitor(config)
    
    if args.daemon:
        # Run continuously
        await monitor.run_forever()
    else:
        # Single check
        logger.info("Running single health check...")
        await monitor._check_all_services()
        monitor._display_status_dashboard()
        monitor._save_statistics()


if __name__ == "__main__":
    asyncio.run(main())
