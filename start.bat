@echo off
SETLOCAL
TITLE Network Flow Defence Launcher

REM --- 1. PREREQUISITE CHECK ---
echo Checking for prerequisites...

REM Set default python command
SET "PYTHON_CMD=python"

REM Check for 'py' command first
py --version >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
    SET "PYTHON_CMD=py"
) ELSE (
    REM If 'py' not found, check for 'python'
    python --version >NUL 2>NUL
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python (as 'py' or 'python') is not installed or not found in your PATH.
        echo Please install Python 3.10 or newer and try again.
        echo.
        pause
        EXIT /B 1
    )
)
echo Found Python as: %PYTHON_CMD%

REM Check for Node.js and npm
npm --version >NUL 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js and npm are not installed or not found in your PATH.
    echo Please install Node.js (which includes npm) and try again.
    echo.
    pause
    EXIT /B 1
)
echo All prerequisites found.
echo.


REM --- 2. BACKEND SETUP (Python / venv) ---
echo [Backend] Setting up Python environment...

REM Check for venv folder
IF NOT EXIST venv (
    echo [Backend] No 'venv' found. Creating one...
    %PYTHON_CMD% -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        echo.
        pause
        EXIT /B 1
    )
    echo [Backend] Virtual environment created.
) ELSE (
    echo [Backend] Existing 'venv' found.
)

REM Activate venv and install requirements
echo [Backend] Activating virtual environment...
CALL venv\Scripts\activate.bat

echo [Backend] Installing Python packages from backend/requirements.txt...
pip install -r backend/requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python requirements.
    echo.
    pause
    EXIT /B 1
)
echo [Backend] Python packages installed.

REM Check for ML model and train if it doesn't exist
IF NOT EXIST backend\ml\models\rf_model.pkl (
    echo [Backend] ML model not found. Running training script...
    echo This may take a minute...
    %PYTHON_CMD% backend/ml/training/train.py
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to train the ML model.
        echo.
        pause
        EXIT /B 1
    )
    echo [Backend] ML model trained successfully.
) ELSE (
    echo [Backend] ML model found.
)
echo [Backend] Python setup complete.
echo.


REM --- 3. FRONTEND SETUP (React / npm) ---
echo [Frontend] Launching new terminal for React app...
REM This command opens a new terminal window, navigates to 'frontend',
REM installs packages, and starts the app. cmd /K keeps it open.
START "Frontend (React)" cmd /K (
    echo [Frontend] Navigating to frontend directory...
    cd frontend
    
    echo [Frontend] Installing/verifying npm dependencies (this may take a moment)...
    npm install
    
    echo [Frontend] Starting React app (npm start)...
    npm start
)

echo [Frontend] React app is launching in a new window...
echo.


REM --- 4. BACKEND LAUNCH (FastAPI / uvicorn) ---
echo [Backend] Launching FastAPI server...
echo This window will show the backend server log.
echo Your app will be available at http://localhost:3000
echo.

uvicorn api.main:app --port 8000 --app-dir backend

pause
ENDLOCAL

