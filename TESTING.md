# Testing Guide

This guide explains how to run tests for the e-harold-krabs Finance Assistant.

## Current Status ✅

- **Unit Tests**: ✅ 26 tests passing
- **Local Testing**: ✅ Working with SQLite database
- **CI/CD Pipeline**: ✅ Automated testing with GitHub Actions
- **Test Organization**: ✅ Clean unit test structure
- **Dependency Management**: ✅ Virtual environment setup

## Quick Start

### Run All Unit Tests Locally
```bash
./run-unit-tests.sh
```

### Run Tests in Docker (CI/CD)
```bash
./run.sh --test
```

### Start Application Locally
```bash
./run.sh
```

## Test Structure

### Unit Tests (`tests/unit_tests/`)
All unit tests are organized in the `tests/unit_tests/` directory:

- `test_config_unit.py` - Configuration validation (7 tests)
- `test_csv_parser_unit.py` - CSV parsing logic (7 tests)
- `test_dashboard_unit.py` - Dashboard logic and data validation (7 tests)
- `test_insights_unit.py` - Financial insights calculations (7 tests)

### Test Infrastructure
- `tests/__init__.py` - Test package initialization
- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/mock_deps.py` - Mock objects for isolated testing
- `tests/test_services.py` - Service layer integration tests
- `pytest.ini` - Pytest configuration with warning filters

## Test Scripts

### Local Testing (Recommended for Development)
```bash
# Run unit tests with SQLite database
./run-unit-tests.sh

# Alternative: Use main script for local testing
./run.sh --local-test
```

### Docker Testing (CI/CD Environment)
```bash
# Run tests in Docker containers with PostgreSQL
./run.sh --test
```

### Development Mode
```bash
# Start the application locally (API + Dashboard)
./run.sh
```

## Test Results Summary

### ✅ All Unit Tests Passing (26/26)
- **Configuration Tests**: 7 tests - Environment variables, API keys, database URLs
- **CSV Parser Tests**: 7 tests - Data parsing, validation, type conversion
- **Dashboard Tests**: 7 tests - Data processing, API configuration, validation
- **Insights Tests**: 7 tests - Financial calculations, balance logic, transaction analysis

### Test Coverage Areas
- ✅ **Core Business Logic**: Financial calculations and data processing
- ✅ **Configuration Management**: Environment variables and settings
- ✅ **Data Validation**: Input validation and error handling
- ✅ **API Integration**: Service layer functionality
- ✅ **Local Development**: SQLite-based testing environment

## Test Configuration

### Local Testing
- **Database**: SQLite (`test.db`) for fast, isolated testing
- **Environment**: Uses `test-config.env` for test-specific configuration
- **Dependencies**: Virtual environment with all required packages

### CI/CD Testing
- **Database**: PostgreSQL in Docker containers
- **Environment**: Uses `.env` file created from `.env.example`
- **Infrastructure**: Docker Compose for containerized testing

## CI/CD Pipeline

Tests are automatically run in GitHub Actions with the following workflow:

1. **Unit Tests Job**: Fast, isolated tests on Ubuntu
   - Sets up Python 3.9 environment
   - Installs dependencies with caching
   - Runs all unit tests with pytest
   - Reports results and coverage

2. **Integration Tests Job**: Full-stack testing
   - Builds Docker images with caching
   - Creates test environment from `.env.example`
   - Runs integration tests in containers
   - Tests API endpoints and Docker Compose setup
   - Cleans up containers automatically

## Troubleshooting

### Common Issues and Solutions

1. **Virtual Environment Issues**
   ```bash
   # Delete and recreate virtual environment
   rm -rf venv/
   ./run-unit-tests.sh
   ```

2. **Import Errors**
   - Ensure `PYTHONPATH` includes the `app/` directory
   - Check that all dependencies are installed in virtual environment

3. **Database Connection Issues**
   - Local testing uses SQLite automatically
   - Docker testing requires PostgreSQL container to be running

4. **Docker Issues**
   - Ensure Docker Desktop is running
   - Check that `docker compose` command is available
   - Try: `docker compose down && docker compose up --build`

5. **Test Failures**
   - Run tests individually: `python -m pytest tests/unit_tests/test_specific.py -v`
   - Check test logs for specific error messages
   - Verify test data and mock objects are correct

### Performance Tips

- **Local Development**: Use `./run-unit-tests.sh` for fastest feedback
- **CI/CD**: Tests run automatically on push/PR to `main` branch
- **Debugging**: Use `pytest -v -s` for verbose output with print statements

## Test Maintenance

### Adding New Tests
1. Place unit tests in `tests/unit_tests/` directory
2. Follow naming convention: `test_feature_unit.py`
3. Use descriptive test method names: `test_calculate_balance_positive_case`
4. Include docstrings explaining test purpose

### Test Dependencies
- **pytest**: Test framework with fixtures and assertions
- **unittest.mock**: Mock objects for isolated testing
- **SQLite**: Local database for fast testing
- **PostgreSQL**: Docker container for integration testing

## File Structure Reference

```
tests/
├── __init__.py
├── conftest.py
├── mock_deps.py
├── test_services.py
└── unit_tests/
    ├── __init__.py
    ├── test_config_unit.py
    ├── test_csv_parser_unit.py
    ├── test_dashboard_unit.py
    └── test_insights_unit.py
```

This structure ensures clean separation between unit tests, integration tests, and test infrastructure.
