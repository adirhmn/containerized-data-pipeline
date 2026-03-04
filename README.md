# Customer Data Pipeline

## Overview

This project implements a **containerized data pipeline** consisting of three services:

1. **Flask Mock Server** – Provides mock customer data via REST API
2. **FastAPI Pipeline Service** – Ingests data from Flask and stores it in PostgreSQL using `dlt`
3. **PostgreSQL Database** – Persistent storage for customer records

Data flow:

```
Flask API (JSON)
        ↓
FastAPI Ingestion Service
        ↓
PostgreSQL Database
        ↓
FastAPI Query API
```

The entire system runs using **Docker Compose**.

---

# Project Structure

```
data-pipeline/
│
├── docker-compose.yml
├── README.md
│
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
│
└── pipeline-service/
    ├── main.py
    ├── database.py
    ├── models/
    │   ├── __init__.py
    │   └── customer.py
    ├── services/
    │   ├── __init__.py
    │   └── ingestion.py
    ├── Dockerfile
    └── requirements.txt
```

---

# Architecture

Services included in the system:

| Service           | Port | Description                      |
| ----------------- | ---- | -------------------------------- |
| Flask Mock Server | 5000 | Provides paginated customer data |
| FastAPI Pipeline  | 8000 | Handles ingestion and API access |
| PostgreSQL        | 5432 | Stores customer records          |

---

# Prerequisites

Ensure the following tools are installed:

- Docker Desktop (running)
- Docker Compose
- Git
- Python 3.10+ (optional for local development)

Verify Docker Compose:

```
docker-compose --version
```

---

# Running the System

Start all services:

```
docker-compose up -d --build
```

Check running containers:

```
docker-compose ps
```

Expected services:

```
postgres
mock-server
pipeline-service
```

Stop services:

```
docker-compose down
```

---

# Flask Mock Server

The Flask service provides customer data stored in a JSON file.

Base URL:

```
http://localhost:5000
```

## Endpoints

### Health Check

```
GET /api/health
```

Example:

```
curl http://localhost:5000/api/health
```

Response:

```
{
  "status": "ok"
}
```

---

### Get Customers (Paginated)

```
GET /api/customers?page=1&limit=5
```

Example:

```
curl http://localhost:5000/api/customers?page=1&limit=5
```

Response:

```
{
  "data": [...],
  "total": 20,
  "page": 1,
  "limit": 5
}
```

---

### Get Customer by ID

```
GET /api/customers/{id}
```

Example:

```
curl http://localhost:5000/api/customers/CUST-0001
```

---

# FastAPI Pipeline Service

Base URL:

```
http://localhost:8000
```

Swagger Documentation:

```
http://localhost:8000/docs
```

---

## Ingest Data from Flask

```
POST /api/ingest
```

This endpoint:

1. Fetches all paginated data from Flask
2. Normalizes data types
3. Loads records into PostgreSQL using `dlt`
4. Performs **merge/upsert** using `customer_id`

Example:

```
curl -X POST http://localhost:8000/api/ingest
```

Response:

```
{
  "status": "success",
  "records_processed": 20
}
```

---

## Get Customers (from Database)

```
GET /api/customers?page=1&limit=5
```

Example:

```
curl http://localhost:8000/api/customers?page=1&limit=5
```

---

## Get Customer by ID

```
GET /api/customers/{id}
```

Example:

```
curl http://localhost:8000/api/customers/CUST-0001
```

---

# Database Schema

Table: **customers**

| Column          | Type          |
| --------------- | ------------- |
| customer_id     | VARCHAR(50)   |
| first_name      | VARCHAR(100)  |
| last_name       | VARCHAR(100)  |
| email           | VARCHAR(255)  |
| phone           | VARCHAR(20)   |
| address         | TEXT          |
| date_of_birth   | DATE          |
| account_balance | DECIMAL(15,2) |
| created_at      | TIMESTAMP     |

Primary Key:

```
customer_id
```

---

# Data Ingestion Process

The ingestion pipeline performs the following steps:

1. Fetch paginated data from Flask API
2. Normalize fields (date, timestamp)
3. Load records using `dlt`
4. Merge data into PostgreSQL

Upsert behavior:

```
write_disposition="merge"
primary_key="customer_id"
```

Existing records are updated, new records are inserted.

---

# Logging

The ingestion service logs important pipeline events:

- Data fetching progress
- Number of records retrieved
- Ingestion start
- Ingestion completion

View logs:

```
docker-compose logs -f pipeline-service
```

---

# Testing

### Test Flask API

```
curl http://localhost:5000/api/customers?page=1&limit=5
```

### Run Data Ingestion

```
curl -X POST http://localhost:8000/api/ingest
```

### Query Database via API

```
curl http://localhost:8000/api/customers?page=1&limit=5
```

---

# Evaluation Criteria

| Component                     | Points  |
| ----------------------------- | ------- |
| Flask Mock Server             | 50      |
| FastAPI Ingestion + Endpoints | 50      |
| Docker Compose                | 20      |
| Documentation                 | 10      |
| Code Quality                  | 10      |
| **Total**                     | **140** |

---

# Submission Checklist

```
[x] All 3 services start with docker-compose up

[x] Flask serves paginated customer data

[x] FastAPI successfully ingests data into PostgreSQL

[x] All API endpoints function correctly
```

---

# Author

Backend Developer Technical Assessment
Customer Data Pipeline Implementation
