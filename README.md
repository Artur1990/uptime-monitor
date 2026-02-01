# Uptime Monitor

Lightweight uptime monitoring service built with Python and Docker.
The service periodically checks availability and latency of HTTP targets,
exposes results via an API, and provides Prometheus-compatible metrics.
Targets can be managed via a CLI without editing configuration files manually.

## Features
- Periodic HTTP checks for multiple targets
- YAML-based configuration
- CLI for managing monitored targets
- REST API endpoints
- Prometheus metrics endpoint (/metrics)
- Structured JSON logging
- Dockerized application
- CI pipeline with linting, tests, and Docker build
- Monitoring stack with Prometheus and Grafana

## Tech Stack
- Python 3
- FastAPI
- httpx
- Docker & Docker Compose
- GitHub Actions
- Prometheus
- Grafana
- Ruff
- Pytest

## Project Structure
app/            Application code  
config/         YAML configuration  
tests/          Unit tests  
.github/        GitHub Actions workflows  
Dockerfile      Docker image definition  
compose.yml     Local container orchestration  
prometheus.yml  Prometheus scrape configuration  

## Configuration
Targets are stored in config/targets.yml.

Example:
interval_seconds: 5  
timeout_seconds: 3  

targets:
- name: google  
  url: https://www.google.com  

## Managing Targets via CLI

Targets can be added without editing YAML files directly.

### Local usage
python3 -m app.manage add --name facebook --url https://facebook.com

### Using Docker
docker compose run --rm uptime-monitor \
  python -m app.manage add --name github --url https://github.com

The configuration file is updated automatically, and the monitoring loop
picks up new targets without restarting the service.

## Running the Service

Using Docker (recommended):
docker compose up --build

Services:
- Uptime Monitor: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## API Endpoints
- GET /health  – service health status
- GET /results – latest monitoring results
- GET /metrics – Prometheus-compatible metrics

## Monitoring and Observability
- Prometheus scrapes metrics from /metrics
- Grafana visualizes availability and latency
- Logs are structured JSON and written to stdout
- Only meaningful events are logged (state changes, high latency, errors)

## CI Pipeline
On every push and pull request, GitHub Actions runs:
- code linting with ruff
- unit tests with pytest
- Docker image build

## Purpose
This project is designed as a DevOps portfolio project and demonstrates:
- containerization
- CI automation
- observability with metrics and logs
- configuration management via CLI
