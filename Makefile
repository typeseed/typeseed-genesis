.PHONY: help venv install test test-cov test-verbose clean lint format

help:
	@echo "TypeSeed Genesis - Available Commands"
	@echo "======================================"
	@echo "make venv          - Create virtual environment"
	@echo "make install       - Install dependencies"
	@echo "make test          - Run tests"
	@echo "make test-cov      - Run tests with coverage report"
	@echo "make test-verbose  - Run tests with verbose output"
	@echo "make clean         - Remove build artifacts and cache"
	@echo "make lint          - Run linters (if configured)"
	@echo "make format        - Format code (if configured)"

venv:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "✓ Virtual environment created"
	@echo "Activate it with: source .venv/bin/activate"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

test:
	@echo "Running tests..."
	pytest

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=. --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated in htmlcov/"

test-verbose:
	@echo "Running tests with verbose output..."
	pytest -v --tb=long

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.pyc
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned up build artifacts and cache"

lint:
	@echo "Linting code..."
	@echo "Note: Install ruff or pylint first"
	@which ruff > /dev/null && ruff check . || echo "ruff not installed"
	
format:
	@echo "Formatting code..."
	@echo "Note: Install black or ruff first"
	@which black > /dev/null && black . || echo "black not installed"
	@which ruff > /dev/null && ruff format . || echo "ruff not installed"

