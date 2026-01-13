from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class EmployeeManagementSystem(Base):
    __tablename__ = 'employee_record'

    Id = Column(Integer, primary_key=True, index = True)
    employee_name = Column(String, nullable=False)
    employee_email = Column(String, unique= True, nullable=False)
    employee_department = Column(String, nullable= False)
    employee_role = Column(String, nullable=False)
    employee_joining_date = Column(DateTime, default=datetime.utcnow, nullable=False)