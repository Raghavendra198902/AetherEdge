# Security Vulnerability Fix Script for AetherEdge
# Auto-generated remediation script for security issues

Write-Host "AetherEdge Security Remediation Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "No virtual environment detected. Activating..." -ForegroundColor Yellow
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        & ".\.venv\Scripts\Activate.ps1"
        Write-Host "Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "Virtual environment not found. Please create one first." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Updating vulnerable dependencies..." -ForegroundColor Yellow

# High Severity Updates
Write-Host "Updating HIGH severity packages:" -ForegroundColor Red
$highSeverityPackages = @(
    "anyio>=4.4.0",
    "fastapi>=0.109.1", 
    "python-jose>=3.4.0",
    "setuptools>=70.0.0",
    "starlette>=0.49.1"
)

foreach ($package in $highSeverityPackages) {
    Write-Host "  - Updating $package" -ForegroundColor White
    pip install --upgrade $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Failed to update $package" -ForegroundColor Red
    } else {
        Write-Host "    Successfully updated $package" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Updating MEDIUM severity packages:" -ForegroundColor DarkYellow
$mediumSeverityPackages = @(
    "requests>=2.32.4",
    "urllib3>=2.5.0", 
    "jinja2>=3.1.6",
    "black>=24.3.0",
    "mkdocs-material>=9.5.32"
)

foreach ($package in $mediumSeverityPackages) {
    Write-Host "  - Updating $package" -ForegroundColor White
    pip install --upgrade $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Failed to update $package" -ForegroundColor Red
    } else {
        Write-Host "    Successfully updated $package" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Generating updated requirements files..." -ForegroundColor Cyan

# Update main requirements files
pip freeze > requirements-updated.txt

Write-Host ""
Write-Host "Summary of Actions Taken:" -ForegroundColor Green
Write-Host "  Updated vulnerable packages" -ForegroundColor Green
Write-Host "  Generated updated requirements files" -ForegroundColor Green  
Write-Host "  Ready for security verification scan" -ForegroundColor Green

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Run snyk test to verify vulnerabilities are fixed" -ForegroundColor White
Write-Host "  2. Test application functionality with updated dependencies" -ForegroundColor White
Write-Host "  3. Update infrastructure security configurations" -ForegroundColor White
Write-Host "  4. Commit updated requirements files to version control" -ForegroundColor White

Write-Host ""
Write-Host "Security remediation script completed!" -ForegroundColor Green
