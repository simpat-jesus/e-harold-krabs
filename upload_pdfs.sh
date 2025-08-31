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

echo "API is ready. Uploading PDFs at rate of 2 per minute..."

# Get all PDF files
pdf_files=()
for pdf in "test data"/*.pdf; do
    if [ -f "$pdf" ]; then
        pdf_files+=("$pdf")
    fi
done

total_files=${#pdf_files[@]}
echo "Found $total_files PDF files to upload"

# Upload in batches of 2 files per minute
batch_size=2
for ((i=0; i<total_files; i+=batch_size)); do
    echo "Processing batch $((i/batch_size + 1))..."
    
    # Upload up to 2 files in this batch
    for ((j=0; j<batch_size && i+j<total_files; j++)); do
        pdf="${pdf_files[i+j]}"
        echo "Uploading $pdf..."
        curl -X POST -F "file=@$pdf" http://localhost:8000/upload-pdf
        echo "Completed upload of $pdf"
    done
    
    # Wait 60 seconds before next batch (unless it's the last batch)
    if ((i + batch_size < total_files)); then
        echo "Waiting 60 seconds before next batch..."
        sleep 60
    fi
done

echo "All PDFs uploaded successfully."
