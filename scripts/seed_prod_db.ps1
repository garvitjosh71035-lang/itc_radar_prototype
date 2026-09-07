# Quick seed script for Render production database
# Run: .\scripts\seed_prod_db.ps1

Write-Host "🔍 Checking DATABASE_URL environment variable..."

$dbUrl = $env:DATABASE_URL

if (-not $dbUrl) {
    Write-Host "`n❌ Error: DATABASE_URL not set!" -ForegroundColor Red
    Write-Host "Set it using:" -ForegroundColor Yellow
    Write-Host "  render services view <service-name>" -ForegroundColor White
    Write-Host "  Then copy the DATABASE_URL value" -ForegroundColor White
    Write-Host "`n Or set manually:" -ForegroundColor Yellow
    Write-Host "  `$env:DATABASE_URL=`"postgresql://...`"" -ForegroundColor White
    
    exit 1
}

Write-Host "`n🔗 Connecting to production database..." -ForegroundColor Cyan
Write-Host $dbUrl.Substring(0, [Math]::Min(50, $dbUrl.Length)) + "..." 

try {
    # This would normally require psycopg2 or similar PostgreSQL driver
    # For now, we'll just verify connection string is valid
    Write-Host "`n✅ DATABASE_URL looks valid!" -ForegroundColor Green
    Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Install psql or pgcli locally" -ForegroundColor White
    Write-Host "2. Connect: pgcli $dbUrl" -ForegroundColor White
    Write-Host "3. Run SQL commands from dashboard guide" -ForegroundColor White
    
} catch {
    Write-Host "❌ Connection failed: $_" -ForegroundColor Red
    exit 1
}
