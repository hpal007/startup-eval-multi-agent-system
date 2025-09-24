.PHONY: help install install-dev test lint format check clean build

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (ruff + mypy)"
	@echo "  format       Format code (ruff)"
	@echo "  check        Run linting and tests"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build the package"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest

test-cov:
	pytest --cov=agents --cov=utils --cov-report=html --cov-report=term

# Linting and formatting
lint:
	ruff check .
	mypy .

format:
	ruff format .
	ruff check . --fix

# Combined checks
check: lint test

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	python -m build
