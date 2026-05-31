@echo off
call "C:\Users\ASUS\Desktop\math-gpt\backend\.venv\Scripts\activate.bat"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
