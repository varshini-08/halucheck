@echo off
cd /d D:\halu
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
