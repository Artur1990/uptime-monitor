# Uptime Monitor
Lightweight uptime monitoring service built with Python, Docker, and GitHub Actions. The service periodically checks availability and latency of configured HTTP targets, exposes results via a REST API, and provides Prometheus-compatible metrics.

## Features
- Periodic HTTP checks for multiple targets
- YAML-based configuration
- REST API endpoints for health and results
- Prometheus metrics endpoint (/metrics)
- Dockerized application
- CI pipeline with linting, tests, and Docker build

## Tech Stack
- Python 3.11
- FastAPI
- httpx
- Docker & Docker Compose
- GitHub Actions
- Prometheus client
- Ruff (linting)
- Pytest (testing)

## Project Structure
app/            # Application code
main.py         # FastAPI application & endpoints
checker.py      # Background checker & metrics
config.py       # Configuration loader
config/         # YAML configuration
tests/          # Unit tests
.github/        # GitHub Actions workflows
Dockerfile      # Docker image definition
compose.yml     # Local container orchestration
pytest.ini      # Pytest configuration

## Configuration
Targets are defined in config/targets.yml:
interval_seconds: 5
timeout_seconds: 3
targets:
- name: google
  url: https://www.google.com
- name: github
  url: https://github.com

## Run Locally (without Docker)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

## Run with Docker
docker compose up --build
The service will be available at http://localhost:8000

## API Endpoints
GET /health – returns service health status
GET /results – returns latest check results for all targets
GET /metrics – Prometheus-compatible metrics endpoint

## CI Pipeline
On every push and pull request, GitHub Actions runs:
- code linting with ruff
- unit tests with pytest
- Docker image build

## Notes
This project is designed as a DevOps portfolio project and demonstrates clean project structure, containerization, CI automation, and basic monitoring and observability.

