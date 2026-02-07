# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
from sqlalchemy import func
from .models import AdminUser
from .security import verify_password

# Authentication
def authenticate_admin(db: Session, username: str, password: str):
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        return None
    if not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin

# Employee CRUD
def create_employee(db: Session, emp: schemas.EmployeeCreate):
    # duplicates validated with exceptions upstream, but double-check
    existing = db.query(models.Employee).filter(
        (models.Employee.employee_id == emp.employee_id) | (models.Employee.email == emp.email)
    ).first()
    if existing:
        raise ValueError("Employee with same ID or email already exists.")
    db_emp = models.Employee(
        employee_id=emp.employee_id,
        full_name=emp.full_name,
        email=emp.email,
        department=emp.department
    )
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def list_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def get_employee(db: Session, emp_id: int):
    return db.query(models.Employee).filter(models.Employee.id == emp_id).first()

def delete_employee(db: Session, emp_id: int):
    emp = get_employee(db, emp_id)
    if not emp:
        return False
    db.delete(emp)
    db.commit()
    return True

# Attendance CRUD
def mark_attendance(db: Session, data: schemas.AttendanceCreate):
    # check employee exists
    emp = db.query(models.Employee).filter(models.Employee.id == data.employee_id).first()
    if not emp:
        raise LookupError("Employee not found")
    # unique per date
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == data.employee_id,
        models.Attendance.date == data.date
    ).first()
    if existing:
        # update existing
        existing.status = data.status
        db.commit()
        db.refresh(existing)
        return existing
    rec = models.Attendance(employee_id=data.employee_id, date=data.date, status=data.status)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_attendance_for_employee(db: Session, employee_id: int, start_date=None, end_date=None):
    q = db.query(models.Attendance).filter(models.Attendance.employee_id == employee_id)
    if start_date and end_date:
        # Both dates provided - show range
        q = q.filter(models.Attendance.date >= start_date)
        q = q.filter(models.Attendance.date <= end_date)
    elif start_date:
        # Only start date - show exact date
        q = q.filter(models.Attendance.date == start_date)
    elif end_date:
        # Only end date - show exact date
        q = q.filter(models.Attendance.date == end_date)
    return q.order_by(models.Attendance.date.desc()).all()

def get_all_attendance(db: Session, start_date=None, end_date=None):
    q = db.query(models.Attendance)
    if start_date and end_date:
        # Both dates provided - show range
        q = q.filter(models.Attendance.date >= start_date)
        q = q.filter(models.Attendance.date <= end_date)
    elif start_date:
        # Only start date - show exact date
        q = q.filter(models.Attendance.date == start_date)
    elif end_date:
        # Only end date - show exact date
        q = q.filter(models.Attendance.date == end_date)
    return q.order_by(models.Attendance.date.desc()).all()

def attendance_summary(db: Session):
    # return total employees and total attendance rows (simple dashboard)
    total_employees = db.query(func.count(models.Employee.id)).scalar()
    total_attendance_rows = db.query(func.count(models.Attendance.id)).scalar()
    return {"total_employees": total_employees, "total_attendance_rows": total_attendance_rows}

def total_present_days_per_employee(db: Session):
    rows = db.query(models.Employee.id, models.Employee.employee_id, models.Employee.full_name, func.count(models.Attendance.id).label("present_days"))\
        .join(models.Attendance, models.Employee.id == models.Attendance.employee_id)\
        .filter(models.Attendance.status == models.Attendance.status.type.python_type.present if False else models.Attendance.status == "Present")\
        .group_by(models.Employee.id).all()
    # simpler: use Enum string
    rows = db.query(models.Employee.id, models.Employee.employee_id, models.Employee.full_name, func.sum(func.case([(models.Attendance.status == 'Present',1)], else_=0)).label("present_days"))\
        .join(models.Attendance, models.Employee.id == models.Attendance.employee_id, isouter=True)\
        .group_by(models.Employee.id).all()
    return [{"id": r[0], "employee_id": r[1], "full_name": r[2], "present_days": int(r[3] or 0)} for r in rows]

def get_present_days_for_employee(db: Session, employee_id: int):
    # Count attendance records where status is 'Present'
    count = db.query(func.count(models.Attendance.id))\
        .filter(models.Attendance.employee_id == employee_id)\
        .filter(models.Attendance.status == 'Present')\
        .scalar()
    return {"present_days": int(count or 0)}
