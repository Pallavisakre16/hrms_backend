# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List
from enum import Enum

class AttendanceStatus(str, Enum):
    Present = "Present"
    Absent = "Absent"

class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)

class EmployeeOut(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

    class Config:
        orm_mode = True

class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: AttendanceStatus

class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: date
    status: AttendanceStatus

    class Config:
        orm_mode = True

class EmployeeWithAttendance(EmployeeOut):
    attendance: List[AttendanceOut] = []

class PresentDaysResponse(BaseModel):
    present_days: int

class DashboardResponse(BaseModel):
    total_employees: int
    total_attendance_rows: int

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
