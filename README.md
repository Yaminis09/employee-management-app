
# Employee Management System (FastAPI)

This repository contains a basic Employee Management System built using FastAPI and SQLAlchemy.

The project includes CRUD operations for managing employee records, data validation using Pydantic, and API tests written with Pytest. SQLite is used as the database.

## Files

- `main.py` – FastAPI application and API endpoints  
- `models.py` – Database models using SQLAlchemy  
- `database.py` – Database configuration  
- `test_employees.py` – Test cases for the API  
- `pytest.ini` – Pytest configuration  

## How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
