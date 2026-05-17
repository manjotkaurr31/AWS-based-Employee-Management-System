# AWS-Based Employee Management System

A cloud-native REST API for managing employee records, built with **FastAPI** and deployed on **AWS ECS (Fargate)** via a fully automated **CI/CD pipeline** using GitHub Actions. Developed with the intent to learn and practice Cloud Network Security Engineering.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [AWS Services Used](#aws-services-used)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [CI/CD Pipeline](#cicd-pipeline)
- [Getting Started](#getting-started)
- [Environment Variables & Secrets](#environment-variables--secrets)
- [Docker](#docker)

---

## Overview

This project is a production-ready **Employee Management System** that exposes a RESTful API to perform full CRUD operations on employee records. It is containerized with Docker, stores secrets securely in **AWS Secrets Manager**, persists data in a **PostgreSQL** database, and is automatically deployed to **AWS ECS** on every push to `main`.

---

## Architecture

```
Developer → GitHub Push (main)
                │
                ▼
        GitHub Actions CI/CD
                │
        ┌───────┴────────┐
        │                │
   Build Docker      Configure AWS
   Image             Credentials
        │
        ▼
   Push to AWS ECR
   (Elastic Container Registry)
        │
        ▼
   Update ECS Task Definition
        │
        ▼
   Deploy to AWS ECS (Fargate)
   [employee-management-cluster]
        │
        ▼
   FastAPI App (port 8000)
        │
        ├── AWS Secrets Manager  ← DB credentials
        └── PostgreSQL (RDS)     ← Employee data
```
<p align="center">
  <img src="./images/architecture.png" width="900">
</p>

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Data Validation | Pydantic |
| ORM / DB Driver | SQLAlchemy, psycopg2 |
| Server | Gunicorn + Uvicorn Worker |
| Containerization | Docker |
| Language | Python 3.11 |

---

## AWS Services Used

| Service | Purpose |
|---|---|
| **ECS (Fargate)** | Runs the containerized FastAPI application |
| **ECR** | Stores Docker images (`employee-api`) |
| **Secrets Manager** | Securely stores the database connection URL (`employee-db-secret`) |
| **RDS (PostgreSQL)** | Persistent storage for employee records |
| **IAM** | Manages credentials for GitHub Actions deployment |

---

## Project Structure

```
AWS-based-Employee-Management-System/
├── app/
│   ├── main.py          # FastAPI app with all route definitions
│   ├── db.py            # Database engine setup via AWS Secrets Manager
│   └── models.py        # Pydantic Employee model
├── .github/
│   └── workflows/
│       └── deploy.yml   # GitHub Actions CI/CD pipeline
├── Dockerfile           # Container definition
└── README.md
```

---

## API Endpoints

### Base URL
```
http://<ECS-PUBLIC-IP-OR-LOAD-BALANCER>:8000
```

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check — returns `{ "status": "running" }` |
| `POST` | `/init-db` | Creates the `employees` table if it doesn't exist |
| `POST` | `/employees` | Add a new employee |
| `GET` | `/employees` | Retrieve all employees |
| `PUT` | `/employees/{emp_id}` | Update an employee by ID |
| `DELETE` | `/employees/{emp_id}` | Delete an employee by ID |

### Request Body (for POST and PUT)

```json
{
  "name": "Jane Doe",
  "role": "Software Engineer"
}
```

### Example Responses

**GET /employees**
```json
[
  { "id": 1, "name": "Jane Doe", "role": "Software Engineer" },
  { "id": 2, "name": "John Smith", "role": "DevOps Engineer" }
]
```

**POST /employees**
```json
{ "message": "employee added" }
```

**PUT /employees/1**
```json
{ "message": "employee updated" }
```

**DELETE /employees/1**
```json
{ "message": "employee deleted" }
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) triggers on every push to the `main` branch and performs the following steps:

1. **Checkout** — Pulls the latest code
2. **Configure AWS Credentials** — Uses secrets stored in GitHub to authenticate with AWS
3. **Login to ECR** — Authenticates Docker with the Elastic Container Registry
4. **Build & Push Image** — Builds the Docker image and pushes it to ECR with the `latest` tag
5. **Download Task Definition** — Fetches the current ECS task definition and strips read-only fields
6. **Render Updated Task Definition** — Injects the new image URI into the task definition
7. **Deploy to ECS** — Registers the new task definition and updates the ECS service, waiting for stability

```
main branch push
      │
      ▼
[Checkout] → [AWS Auth] → [ECR Login]
      │
      ▼
[Docker Build & Push to ECR]
      │
      ▼
[Fetch & Clean Task Definition]
      │
      ▼
[Render New Task Def with Latest Image]
      │
      ▼
[Deploy to ECS → wait-for-service-stability]
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker
- AWS CLI configured with appropriate permissions
- An AWS account with ECS, ECR, RDS, and Secrets Manager set up

### Run Locally

1. SSH into EC2 Instance

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn gunicorn sqlalchemy psycopg2-binary boto3
   ```

3. **Set up AWS Secrets Manager**

   Create a secret named `employee-db-secret` in `ap-south-1` with the following structure:
   ```json
   {
     "DATABASE_URL": "postgresql://user:password@your-rds-endpoint:5432/dbname"
   }
   ```

4. **Run the app**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Containerize and Run with Docker

```bash
docker build -t employee-api .
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=<your-key> \
  -e AWS_SECRET_ACCESS_KEY=<your-secret> \
  -e AWS_DEFAULT_REGION=ap-south-1 \
  employee-api
```

---

## Environment Variables & Secrets

The application does **not** use `.env` files for database credentials. Instead, it fetches them securely at runtime from **AWS Secrets Manager**.

| Secret Name | Key | Description |
|---|---|---|
| `employee-db-secret` | `DATABASE_URL` | Full PostgreSQL connection string |

GitHub Actions requires the following **repository secrets** for CI/CD:

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key with ECS/ECR/Secrets permissions |
| `AWS_SECRET_ACCESS_KEY` | Corresponding IAM secret key |

---

## Docker

The `Dockerfile` uses a slim Python 3.11 base image and serves the app via Gunicorn with Uvicorn workers for production-grade async performance.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app/ /app/app/
RUN pip install --no-cache-dir fastapi uvicorn gunicorn sqlalchemy psycopg2-binary boto3
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
```

- **2 Gunicorn workers** for concurrent request handling
- Runs on **port 8000**
- No dev dependencies included

---
