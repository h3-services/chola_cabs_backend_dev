@echo off
echo Starting Cab Booking API Server...
echo.

REM Start the server in background
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM Wait for server to start
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

REM Run the tests
echo.
echo Running API Tests...
echo.
python quick_api_test.py

echo.
echo Press any key to stop the server...
pause > nul

REM Kill the server
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
