from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import Base, engine, get_db
from models.customer import Customer
from services.ingestion import fetch_all_customers, run_dlt_upsert

app = FastAPI(title="Pipeline Service")

@app.on_event("startup")
def on_startup():
    # Pastikan tabel untuk query endpoint tersedia
    Base.metadata.create_all(bind=engine)

@app.post("/api/ingest")
def ingest():
    try:
        customers = fetch_all_customers(page_size=10)  # sengaja kecil biar terbukti pagination jalan
        processed = run_dlt_upsert(customers)
        return {"status": "success", "records_processed": processed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    total = db.query(Customer).count()
    rows = db.execute(
        select(Customer).order_by(Customer.customer_id).offset(offset).limit(limit)
    ).scalars().all()

    data = [
        {
            "customer_id": r.customer_id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "email": r.email,
            "phone": r.phone,
            "address": r.address,
            "date_of_birth": r.date_of_birth.isoformat() if r.date_of_birth else None,
            "account_balance": float(r.account_balance) if r.account_balance is not None else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

    return {"data": data, "total": total, "page": page, "limit": limit}

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer_id": row.customer_id,
        "first_name": row.first_name,
        "last_name": row.last_name,
        "email": row.email,
        "phone": row.phone,
        "address": row.address,
        "date_of_birth": row.date_of_birth.isoformat() if row.date_of_birth else None,
        "account_balance": float(row.account_balance) if row.account_balance is not None else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }