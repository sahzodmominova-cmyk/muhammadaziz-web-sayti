@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)

if not exist .venv (
    echo [1/3] Virtual muhit yaratilmoqda...
    %PY% -m venv .venv
)

echo [2/3] Kutubxonalar o'rnatilmoqda...
call .venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

set ADMIN_PASSWORD=admin123

echo [3/3] Sayt ishga tushmoqda: http://127.0.0.1:5000
echo Admin panel: http://127.0.0.1:5000/admin  (parol: admin123)
echo To'xtatish uchun Ctrl+C bosing.
start "" http://127.0.0.1:5000
python app.py
pause
