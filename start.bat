@echo off
echo Starting Backend...
start cmd /k "cd backend && call .venv\Scripts\activate && uvicorn app.main:app --reload"

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo Application started! The frontend and backend are running in new windows.
