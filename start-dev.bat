@echo off
echo Starting BuzzBus development environment...

echo Starting .NET API...
start "BuzzBus API" cmd /k "cd BuzzBus.Api && dotnet run"

timeout /t 3 /nobreak >nul

echo Starting React app...
start "BuzzBus React" cmd /k "npm start"

echo Both services are starting...
echo React app: http://localhost:3000
echo .NET API: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul
