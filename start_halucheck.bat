@echo off
cd /d D:\halu
start "HaluCheck API" cmd /k "call start_backend.bat"
start "HaluCheck React" cmd /k "call start_frontend.bat"
echo HaluCheck backend: http://127.0.0.1:8000
echo HaluCheck frontend: http://localhost:5173
