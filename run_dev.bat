@echo off
echo ========================================================
echo       Starting LearnForge AI Development Servers
echo ========================================================
echo.
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "LearnForge AI Backend" cmd /k "cd backend && ..\..\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching React Vite Frontend on http://localhost:5173 ...
start "LearnForge AI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers initiated!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo Demo Student Login: student@learnforge.ai / password123
echo ========================================================
pause
