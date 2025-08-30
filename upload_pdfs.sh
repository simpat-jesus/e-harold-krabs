#!/bin/bash

# Start containers
echo "Starting containers..."
docker-compose up --build -d

# Wait for API to be ready
echo "Waiting for API to be ready..."
sleep 30  # Adjust as needed

# Check if API is up
until curl -f http://localhost:8000/docs > /dev/null 2>&1; do
    echo "API not ready, waiting..."
    sleep 5
done

echo "API is ready. Uploading PDFs in parallel..."

# Upload each PDF in parallel
pids=()
for pdf in "test data"/*.pdf; do
    if [ -f "$pdf" ]; then
        echo "Uploading $pdf..."
        curl -X POST -F "file=@$pdf" http://localhost:8000/upload-pdf &
        pids+=($!)
    fi
done

# Wait for all uploads to finish
for pid in "${pids[@]}"; do
    wait "$pid"
done

echo "All PDFs uploaded."
