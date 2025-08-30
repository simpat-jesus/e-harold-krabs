#!/bin/bash

echo "🧪 Running e-harold-krabs Unit Tests Locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Handle problematic dependencies gracefully
echo "🔧 Handling dependency compatibility issues..."
pip install --upgrade --force-reinstall cryptography || echo "⚠️  Cryptography upgrade failed, continuing..."
pip install --upgrade --force-reinstall cffi || echo "⚠️  CFFI upgrade failed, continuing..."

# Load test configuration
if [ -f "test-config.env" ]; then
    echo "📋 Loading test configuration..."
    set -a
    source test-config.env
    set +a
fi

# Set up environment variables for testing (with fallbacks)
export TESTING=${TESTING:-true}
export DATABASE_URL=${TEST_DATABASE_URL:-"sqlite:///./test.db"}
export OPENAI_API_KEY=${TEST_OPENAI_API_KEY:-"test_key_for_local_testing"}
export PYTHONPATH="$PWD/app:$PYTHONPATH"

# Create test database directory if it doesn't exist
mkdir -p tests

# Run unit tests locally (start with working tests)
echo "🧪 Running unit tests locally..."
echo "📊 Test Database: $DATABASE_URL"
echo "🔧 Python Path: $PYTHONPATH"

# Run only the pure unit tests (treat warnings as errors, but disable warnings plugin for now)
python -m pytest tests/unit_tests/ -v --tb=short -W error -p no:warnings

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ Unit tests passed!"
    
    # All unit tests completed successfully
    echo "🎉 All unit tests completed successfully!"
    
else
    echo "❌ Core tests failed!"
    exit 1
fi

echo "🎉 Unit test run complete!"
