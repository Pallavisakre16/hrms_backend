# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base
from typing import List, Optional
from datetime import date
import uvicorn
from .models import create_default_admin
from fastapi.security import OAuth2PasswordRequestForm
from .security import create_access_token
from .dependencies import get_current_admin

Base.metadata.create_all(bind=engine)
app = FastAPI(title="HRMS Lite API", version="1.0")


origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_default_admin(db)
    finally:
        db.close()

@app.post("/admin/login", response_model=schemas.Token)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = crud.authenticate_admin(db, form_data.username, form_data.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": admin.username, "role": "admin"}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Employee endpoints
@app.post("/employees", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    try:
        created = crud.create_employee(db, emp)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/employees", response_model=List[schemas.EmployeeOut])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_employees(db, skip=skip, limit=limit)

@app.delete("/employees/{employee_id}", status_code=204)
def remove_employee(employee_id: int, db: Session = Depends(get_db)):
    success = crud.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return

@app.get("/employees/{employee_id}/attendance", response_model=List[schemas.AttendanceOut])
def get_employee_attendance(employee_id: int, start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    emp = crud.get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.get_attendance_for_employee(db, employee_id, start_date, end_date)

# Attendance endpoints
@app.post("/attendance", response_model=schemas.AttendanceOut, status_code=201)
def post_attendance(att: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    try:
        rec = crud.mark_attendance(db, att)
        return rec
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/attendance", response_model=List[schemas.AttendanceOut])
def get_all_attendance(start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None), db: Session = Depends(get_db)):
    return crud.get_all_attendance(db, start_date, end_date)

# Dashboard and bonus endpoints
@app.get("/dashboard", response_model=schemas.DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return crud.attendance_summary(db)

@app.get("/present-days")
def present_days(db: Session = Depends(get_db)):
    return crud.total_present_days_per_employee(db)

@app.get("/employees/{employee_id}/present-days", response_model=schemas.PresentDaysResponse)
def get_employee_present_days(employee_id: int, db: Session = Depends(get_db)):
    try:
        emp = crud.get_employee(db, employee_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        result = crud.get_present_days_for_employee(db, employee_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with Uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
