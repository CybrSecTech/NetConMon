@echo off
setlocal enabledelayedexpansion

:: Check if running with administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo Please run this installer as administrator
    echo Right-click the install.bat file and select "Run as administrator"
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python is installed. Checking version...
    for /f "tokens=2 delims= " %%i in ('python --version') do set pyver=%%i
    echo Found Python version !pyver!
) else (
    echo Python is not installed.
    echo Would you like to download Python? [Y/N]
    set /p choice=
    if /i "!choice!"=="Y" (
        echo Opening Python download page...
        start https://www.python.org/downloads/
        echo.
        echo Please:
        echo 1. Download and install Python 3.7 or higher
        echo 2. IMPORTANT: Check "Add Python to PATH" during installation
        echo 3. After installation completes, close this window and run install.bat again
        pause
        exit /b 1
    ) else (
        echo Installation cancelled
        pause
        exit /b 1
    )
)

:: Check pip installation
python -m pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo pip is installed
) else (
    echo Installing pip...
    python -m ensurepip --upgrade
    if %errorLevel% == 0 (
        echo pip installed successfully
    ) else (
        echo Failed to install pip
        pause
        exit /b 1
    )
)

:: Install required packages
echo.
echo Installing required packages...
python -m pip install -r requirements.txt
if %errorLevel% == 0 (
    echo Packages installed successfully
) else (
    echo Failed to install required packages
    pause
    exit /b 1
)

:: Create backups directory
if not exist "backups" (
    mkdir "backups"
    echo Created backups directory
)

echo.
echo Installation completed successfully!
echo.
echo To run NetConMon:
echo 1. Right-click on netconmongui.py
echo 2. Select "Run as administrator"
echo.
echo Press any key to exit...
pause
exit /b 0