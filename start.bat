@echo off
echo =====================================================================
echo  MathGPT: Graph-Enhanced RAG Intelligent Mathematical Learning Platform
echo =====================================================================

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not in PATH. Trying local AppData Python...
    set PYTHON_BIN="%LOCALAPPDATA%\Python\bin\python.exe"
) else (
    set PYTHON_BIN=python
)

echo [1/2] Starting MathGPT FastAPI Backend on http://localhost:8000 ...
start "MathGPT Backend" cmd /k "cd /d %~dp0backend && %PYTHON_BIN% -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React + Vite Frontend on http://localhost:5173 ...
start "MathGPT Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo =====================================================================
echo  MathGPT is launching!
echo  Backend Docs:  http://localhost:8000/docs
echo  Frontend UI:   http://localhost:5173
echo =====================================================================
