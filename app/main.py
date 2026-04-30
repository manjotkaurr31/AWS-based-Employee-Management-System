from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.db import engine
from app.models import Employee

app = FastAPI()


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/init-db")
def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name TEXT,
                role TEXT
            )
        """))
    return {"message": "table created"}


@app.post("/employees")
def create_employee(emp: Employee):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO employees (name, role) VALUES (:name, :role)"),
            {"name": emp.name, "role": emp.role}
        )
    return {"message": "employee added"}


@app.get("/employees")
def get_employees():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM employees"))
        data = [dict(row._mapping) for row in result]

    if not data:
        raise HTTPException(status_code=404, detail="No employees found")

    return data


@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, emp: Employee):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE employees
                SET name = :name, role = :role
                WHERE id = :id
            """),
            {"name": emp.name, "role": emp.role, "id": emp_id}
        )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "employee updated"}


@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int):
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM employees WHERE id = :id"),
            {"id": emp_id}
        )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "employee deleted"}
