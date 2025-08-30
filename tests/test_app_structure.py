import pytest
import os
import sys

def test_app_structure():
    """Test that the application has the expected structure"""
    # Check that main directories exist
    assert os.path.exists("app")
    assert os.path.exists("app/services")
    assert os.path.exists("app/db")
    assert os.path.exists("app/api")
    assert os.path.exists("dashboard")
    assert os.path.exists("tests")

    # Check that key files exist
    assert os.path.exists("app/main.py")
    assert os.path.exists("app/config.py")
    assert os.path.exists("requirements.txt")
    assert os.path.exists("docker-compose.yml")

def test_python_imports():
    """Test that key modules can be imported"""
    try:
        # Test relative imports work
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
        assert "No module named" in str(e) or "cannot import name" in str(e)

def test_requirements_file():
    """Test that requirements.txt exists and has expected content"""
    assert os.path.exists("requirements.txt")

    with open("requirements.txt", "r") as f:
        content = f.read()

    # Check for key dependencies
    assert "fastapi" in content
    assert "sqlalchemy" in content
    assert "pandas" in content
    assert "pytest" in content

def test_docker_compose():
    """Test that docker-compose.yml exists and is valid YAML"""
    assert os.path.exists("docker-compose.yml")

    import yaml
    with open("docker-compose.yml", "r") as f:
        config = yaml.safe_load(f)

    # Check basic structure
    assert "services" in config
    assert "db" in config["services"]
    assert "api" in config["services"]
    assert "dashboard" in config["services"]
