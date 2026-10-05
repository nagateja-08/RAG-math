@echo off
echo Starting Backend...
start cmd /k "cd backend && call .venv\Scripts\activate && uvicorn app.main:app --reload"

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo Both servers started!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
