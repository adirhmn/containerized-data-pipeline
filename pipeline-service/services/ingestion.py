import os
import requests
import dlt
from datetime import datetime
from dlt.destinations import postgres

MOCK_BASE_URL = os.environ.get("MOCK_BASE_URL", "http://localhost:5000")
DATABASE_URL = os.environ.get("DATABASE_URL")


def normalize_customer(row: dict) -> dict:
    """
    Normalize customer fields so they match PostgreSQL column types.
    This prevents type mismatch errors during ingestion.
    """
    customer = dict(row)

    # Convert date_of_birth string -> Python date object
    dob = customer.get("date_of_birth")
    if isinstance(dob, str) and dob:
        try:
            customer["date_of_birth"] = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            customer["date_of_birth"] = None

    # Convert created_at string -> Python datetime object (if present)
    created = customer.get("created_at")
    if isinstance(created, str) and created:
        try:
            created_clean = created.replace("Z", "+00:00")
            customer["created_at"] = datetime.fromisoformat(created_clean)
        except ValueError:
            customer["created_at"] = None

    return customer


def fetch_all_customers(page_size: int = 50):
    """
    Automatically fetch all customer records from the Flask API
    by iterating through paginated responses.
    """
    page = 1
    all_rows = []

    while True:
        r = requests.get(
            f"{MOCK_BASE_URL}/api/customers",
            params={"page": page, "limit": page_size},
            timeout=10
        )

        r.raise_for_status()
        payload = r.json()

        rows = payload.get("data", [])
        if not rows:
            break

        # Normalize each record before storing
        normalized_rows = [normalize_customer(row) for row in rows]
        all_rows.extend(normalized_rows)

        total = payload.get("total", 0)

        # Stop fetching if all records are collected
        if len(all_rows) >= total:
            break

        page += 1

    return all_rows


def run_dlt_upsert(customers: list[dict]) -> int:
    """
    Load customer records into PostgreSQL using dlt.

    Uses merge (upsert) strategy with customer_id as the primary key.
    Existing records will be updated, new records will be inserted.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is required")

    dest = postgres(credentials=DATABASE_URL)

    pipeline = dlt.pipeline(
        pipeline_name="customer_ingestion",
        destination=dest,
        dataset_name="public"
    )

    resource = dlt.resource(
        customers,
        name="customers",
        primary_key="customer_id",
        write_disposition="merge"
    )

    pipeline.run(resource)

    # Return number of processed records
    return len(customers)