# HRMS Lite

**Lightweight Human Resource Management System (HRMS Lite)**  
Frontend: React + Vite + Tailwind  
Backend: FastAPI + SQLAlchemy (SQLite)  

## Live demo
> Add your deployed frontend URL here after you deploy (Vercel / Netlify).  
> Add your backend API URL here after you deploy (Render / Railway).

## Features
- Add / list / delete employees (unique employee ID, valid email).
- Mark attendance per employee (date + Present/Absent). Unique per employee-date.
- View attendance per employee; filter by date range.
- Dashboard: total employees and attendance counts.
- Bonus: total present days per employee endpoint.

## Tech stack
- Frontend: React, Vite, Tailwind CSS, Axios
- Backend: FastAPI, SQLAlchemy, SQLite (easy demo). Swap to Postgres in production.
- Deploy: Frontend — Vercel/Netlify; Backend — Render/Railway/Heroku.

## Run locally (recommended)
### Backend
```bash
python -m venv env_hrms
source env_hrms/bin/activate      # or env_hrms\Scripts\activate on Windows
pip install -r requirements.txt

# start

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# OR
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
# API docs: http://localhost:8000/docs
