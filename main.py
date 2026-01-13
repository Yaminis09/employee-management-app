from fastapi import FastAPI, Depends, HTTPException, status, Path, Query, Header
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from database import engine, SessionLocal
from models import EmployeeManagementSystem
import models

from pydantic import BaseModel, EmailStr, field_validator
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

IST = ZoneInfo("Asia/Kolkata")

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]

security = HTTPBearer()

FAKE_TOKEN = "my-secret-token"

# Pydantic class for employee validation
class EmployeeValidation(BaseModel):
    employee_name: str
    employee_email: EmailStr
    employee_department: Optional[str] = None
    employee_role: Optional[str] = None
    employee_joining_date: datetime

    @field_validator("employee_joining_date")
    @classmethod
    def joining_date_cannot_be_future(cls, value: datetime):
        # Convert incoming date to IST if timezone not provided
        if value.tzinfo is None:
            value = value.replace(tzinfo=IST)

        current_ist_time = datetime.now(IST)

        if value > current_ist_time:
            raise ValueError("employee_joining_date cannot be in the future (IST)")

        return value

# Pydantic Update class
class EmployeeUpdate(BaseModel):
    employee_department: str

# Authorisation
def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )

    if credentials.credentials != FAKE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return True


# Create an Employee
@app.post("/employee", status_code=status.HTTP_201_CREATED)
def create_employee(db: db_dependency, new_record: EmployeeValidation,auth: bool = Depends(verify_token)):
    if new_record.employee_department is not None:
        if not new_record.employee_department.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="employee_department cannot be empty"
            )

    employee = EmployeeManagementSystem(**new_record.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee

# List all Employees
# @app.get("/employee")
# def read_all_employee(db:db_dependency):
#     all_employee = db.query(EmployeeManagementSystem).all()
#     return all_employee

@app.get("/employee")
def read_all_employee(
    db: db_dependency,
    page: int = Query(1, gt=0),
    auth: bool = Depends(verify_token)
):
    limit = 10
    offset = (page - 1) * limit

    employees = (
        db.query(EmployeeManagementSystem)
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_employees = db.query(EmployeeManagementSystem).count()
    total_pages = (total_employees + limit - 1) // limit

    return {
        "page": page,
        "per_page": limit,
        "total_employees": total_employees,
        "total_pages": total_pages,
        "data": employees
    }

# Read employee by id
@app.get("/employee/{id}")
def read_employee_by_id(
    db: db_dependency,
    id: int = Path(gt=0)
):
    employee = db.query(EmployeeManagementSystem)\
                 .filter(EmployeeManagementSystem.Id == id)\
                 .first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee

# Read employee by department
@app.get("/employee/department/{employee_department}")
def read_employee_by_department(db:db_dependency,employee_department:str):
    employee_by_department = db.query(EmployeeManagementSystem).filter(EmployeeManagementSystem.employee_department == employee_department).all()

    if employee_by_department is None:
        raise HTTPException(status_code=404, detail = "Department not found")
    
    return employee_by_department

# Update employee department
@app.put("/employee/{id}")
def update_employee_department(
    db: db_dependency,
    id: int = Path(gt=0),
    update_data: EmployeeUpdate = ...
, auth: bool = Depends(verify_token)):
    employee = db.query(EmployeeManagementSystem)\
                 .filter(EmployeeManagementSystem.Id == id)\
                 .first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Update only department
    employee.employee_department = update_data.employee_department

    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee department updated successfully",
        "employee": employee
    }


# Delete employee record
@app.delete("/employee/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    db: db_dependency,
    id: int = Path(gt=0),auth: bool = Depends(verify_token)
):
    employee = db.query(EmployeeManagementSystem)\
                 .filter(EmployeeManagementSystem.Id == id)\
                 .first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": f"Employee with id {id} deleted successfully"}
