# PowerShell script to run e-harold-krabs Finance Assistant

Write-Host "🚀 Starting e-harold-krabs Finance Assistant..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Start PostgreSQL (if using local, otherwise use docker)
# For local development, ensure PostgreSQL is running
# For docker, use: docker-compose up -d db

# Start API
Write-Host "Starting API server..."
$apiJob = Start-Job -ScriptBlock {
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Start Dashboard
Write-Host "Starting Dashboard..."
$dashboardJob = Start-Job -ScriptBlock {
    streamlit run dashboard/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
}

Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host "📊 API: http://localhost:8000"
Write-Host "📈 Dashboard: http://localhost:8501"
Write-Host "Press Ctrl+C to stop all services"

# Wait for jobs
try {
    Wait-Job -Job $apiJob, $dashboardJob
} finally {
    Write-Host "Stopping services..."
    Stop-Job -Job $apiJob, $dashboardJob
    Remove-Job -Job $apiJob, $dashboardJob
}
