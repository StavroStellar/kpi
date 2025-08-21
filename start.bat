echo [1/4] Checking virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create venv. Make sure Python is installed.
        pause
        exit /b 1
    )
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate

echo [3/4] Installing dependencies...
if exist requirements.txt (
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install packages.
        pause
        exit /b 1
    )
) else (
    echo Error: requirements.txt not found.
    pause
    exit /b 1
)

echo [4/4] Starting Flask app...
set FLASK_APP=main.py
flask run --host=127.0.0.1 --port=5000

echo.
echo Application stopped.
pause