# Cloud Integration Automation Platform

## Overview

A production-ready API integration platform that fetches, transforms, and stores
data across services.

## Architecture

```
Client → FastAPI → External API → Processing → PostgreSQL
```

## Features

- API ingestion pipeline
- Data transformation
- Persistent storage (PostgreSQL)
- Dockerized deployment
- CI/CD via GitHub Actions

## Run Locally

```bash
# Using Docker Compose (recommended – starts app + PostgreSQL)
docker compose up --build

# Or build and run the image manually (requires a running PostgreSQL instance)
docker build -t integration-app .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@localhost:5432/integration_db \
  integration-app
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Path          | Description                                              |
|--------|---------------|----------------------------------------------------------|
| GET    | `/`           | Health check                                             |
| GET    | `/fetch-data` | Fetch & transform data from the external API             |
| POST   | `/store-data` | Fetch, transform, and persist data to PostgreSQL         |

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI application & route handlers
│   ├── database.py    # SQLAlchemy engine & session factory
│   ├── models.py      # ORM models
│   └── transform.py   # Data transformation logic
├── tests/
│   ├── test_main.py
│   └── test_transform.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## CI/CD (GitHub Actions)

The workflow in `.github/workflows/ci.yml` runs on every push and pull request:
1. Installs Python dependencies
2. Executes the test suite
3. Builds the Docker image

## Cloud Deployment (AWS)

- Deploy the container to **ECS** (Fargate) or **EC2**
- Use **RDS (PostgreSQL)** and set the `DATABASE_URL` environment variable

## Real-World Scenario

Simulates SaaS data syncing between platforms — ingesting posts from an upstream
service, normalising them, and storing them for downstream consumption.
