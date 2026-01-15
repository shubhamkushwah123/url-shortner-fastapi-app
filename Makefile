.PHONY: help test test-unit test-integration test-regression test-all test-cov clean lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-regression - Run regression tests only"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  test-smoke   - Run quick smoke tests"
	@echo "  clean        - Clean test artifacts"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run all tests
test:
	pytest

# Run unit tests only
test-unit:
	pytest tests/test_models.py -v

# Run integration tests only
test-integration:
	pytest tests/test_api.py tests/test_integration.py -v

# Run regression tests only
test-regression:
	pytest tests/test_regression.py -v

# Run smoke tests (quick validation)
test-smoke:
	pytest -m "smoke" -v

# Run tests with coverage
test-cov:
	pytest --cov=models --cov=api --cov=main --cov-report=html --cov-report=term

# Run tests with coverage and generate XML report
test-cov-xml:
	pytest --cov=models --cov=api --cov=main --cov-report=xml --cov-report=term

# Clean test artifacts
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run linting (if you add linting tools)
lint:
	@echo "Linting not configured. Add flake8, black, or mypy if needed."

# Format code (if you add formatting tools)
format:
	@echo "Formatting not configured. Add black or autopep8 if needed."

# Run tests in Docker
test-docker:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Development server
dev:
	uvicorn main:app --reload

# Production server
prod:
	docker compose --profile production up --build
