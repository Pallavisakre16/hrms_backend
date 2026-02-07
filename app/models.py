# backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
import enum
from .database import Base
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .security import hash_password

class AttendanceStatus(str, enum.Enum):
    present = "Present"
    absent = "Absent"

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    department = Column(String, nullable=False)

    attendance = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    employee = relationship("Employee", back_populates="attendance")

    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='_employee_date_uc'),
    )

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, default="admin")
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)



def create_default_admin(db):
    # admin = db.query(AdminUser).filter_by(username="admin").first()
    # if admin:
    #     return
    try:
        admin = AdminUser(
            username="admin",
            email="admin@yopmail.com",
            password_hash=hash_password("admin@123")
        )
        db.add(admin)
        db.commit()
    except IntegrityError:
        db.rollback()