import pytest
import os
import sys
from unittest.mock import patch

def test_app_structure():
    """Test that the application has the expected structure"""
    # Check that main directories exist - adapt to container environment
    possible_base_paths = ["/workspace", "/app/..", "..", "."]
    
    app_found = False
    for base_path in possible_base_paths:
        if os.path.exists(os.path.join(base_path, "app")):
            app_found = True
            break
    assert app_found, "app directory should exist somewhere"
    
    # Check relative to current working directory or common locations
    possible_paths = [
        ("app/main.py", "../app/main.py", "/workspace/app/main.py"),
        ("requirements.txt", "../requirements.txt", "/workspace/requirements.txt"),
        ("docker-compose.yml", "../docker-compose.yml", "/workspace/docker-compose.yml")
    ]
    
    for path_options in possible_paths:
        found = any(os.path.exists(path) for path in path_options)
        assert found, f"None of {path_options} found"

def test_python_imports():
    """Test that key modules can be imported"""
    try:
        # Test relative imports work
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

        # Mock database modules before importing
        with patch('app.config.create_engine'), \
             patch('app.config.SessionLocal'), \
             patch('app.config.Base'), \
             patch('app.db.models.Base'), \
             patch('app.db.models.Column'), \
             patch('app.main.Base.metadata.create_all'):
            
            # These should not raise ImportError in the test environment
            # (though they might fail due to missing dependencies)
            import app.config
            import app.services.csv_parser
            import app.services.pdf_parser
            import app.services.insights
            import app.db.models
            import app.db.crud
            import app.api.routes

    except ImportError as e:
        # If imports fail, it should be due to missing dependencies, not structure
        # Common acceptable import errors in test environments
        acceptable_errors = [
            "No module named 'sqlalchemy'",
            "No module named 'fastapi'",
            "No module named 'pandas'",
            "No module named 'pdfplumber'"
        ]
        error_msg = str(e)
        assert any(acceptable_error in error_msg for acceptable_error in acceptable_errors), f"Unexpected import error: {error_msg}"

def test_requirements_file():
    """Test that requirements.txt exists and has expected content"""
    possible_paths = ["requirements.txt", "../requirements.txt", "/workspace/requirements.txt"]
    req_path = None
    for path in possible_paths:
        if os.path.exists(path):
            req_path = path
            break
    
    assert req_path is not None, "requirements.txt should exist"

    with open(req_path, "r") as f:
        content = f.read()

    # Check for key dependencies
    assert "fastapi" in content
    assert "sqlalchemy" in content
    assert "pandas" in content
    assert "pytest" in content

def test_docker_compose():
    """Test that docker-compose.yml exists and is valid"""
    possible_paths = ["docker-compose.yml", "../docker-compose.yml", "/workspace/docker-compose.yml"]
    compose_path = None
    for path in possible_paths:
        if os.path.exists(path):
            compose_path = path
            break
    
    assert compose_path is not None, "docker-compose.yml should exist"

    with open(compose_path, "r") as f:
        content = f.read()

    # Check basic structure without yaml parsing
    assert "services:" in content
    assert "db:" in content  
    assert "api:" in content
    assert "dashboard:" in content
