@echo off
cd /d "%~dp0"
"C:\Users\karan\AppData\Local\Programs\Python\Python39\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
