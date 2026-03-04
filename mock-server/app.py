import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")

def load_customers():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/customers")
def get_customers():
    customers = load_customers()

    # query params
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    total = len(customers)
    start = (page - 1) * limit
    end = start + limit
    data = customers[start:end]

    return jsonify({
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    })

@app.get("/api/customers/<customer_id>")
def get_customer(customer_id: str):
    customers = load_customers()
    found = next((c for c in customers if c.get("customer_id") == customer_id), None)
    if not found:
        return jsonify({"detail": "Customer not found"}), 404
    return jsonify(found)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)