@echo off
echo Starting BuzzBus development environment...

echo Starting FastAPI backend...
start "BuzzBus API" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload"

timeout /t 3 /nobreak >nul

echo Starting React app...
start "BuzzBus React" cmd /k "npm start"

echo Both services are starting...
echo React app: http://localhost:3000
echo FastAPI backend: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul
