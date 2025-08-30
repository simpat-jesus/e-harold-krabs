#!/bin/bash

echo "🚀 Starting e-harold-krabs Finance Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start PostgreSQL (if using local, otherwise use docker)
# For local development, ensure PostgreSQL is running
# For docker, use: docker-compose up -d db

# Start API
echo "Starting API server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start Dashboard
echo "Starting Dashboard..."
streamlit run dashboard/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

echo "✅ Services started!"
echo "📊 API: http://localhost:8000"
echo "📈 Dashboard: http://localhost:8501"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $API_PID $DASHBOARD_PID; exit" INT
wait
