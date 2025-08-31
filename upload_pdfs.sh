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

echo "API is ready. Uploading PDFs sequentially..."

# Get all PDF files
pdf_files=()
for pdf in "test data"/*.pdf; do
    if [ -f "$pdf" ]; then
        pdf_files+=("$pdf")
    fi
done

total_files=${#pdf_files[@]}
echo "Found $total_files PDF files to upload"

if [ $total_files -eq 0 ]; then
    echo "No PDF files found in 'test data' directory. Exiting."
    exit 1
fi

# Upload files sequentially, one at a time
for ((i=0; i<total_files; i++)); do
    pdf="${pdf_files[i]}"
    echo "Uploading $pdf... ($((i+1))/$total_files)"

    # Upload the file and capture both response and HTTP code
    # Use proper quoting for file paths with spaces
    response=$(curl -s --max-time 300 -w "\n%{http_code}" -X POST -F "file=@\"$pdf\"" http://localhost:8000/upload-pdf 2>/dev/null)
    curl_exit_code=$?

    if [ $curl_exit_code -ne 0 ]; then
        echo "✗ Failed to upload $pdf (curl error: $curl_exit_code)"
        continue
    fi

    # Extract response body and HTTP code safely
    response_body=$(echo "$response" | sed '$d')
    http_code=$(echo "$response" | tail -n 1)

    if [ "$http_code" -eq 200 ]; then
        echo "✓ Successfully uploaded $pdf"
        # Optional: Add a small delay between uploads to be gentle on the server
        sleep 2
    else
        echo "✗ Failed to upload $pdf (HTTP $http_code)"
        echo "Response: $response_body"
        # Continue with next file instead of stopping
    fi
done

echo "All PDFs uploaded."
