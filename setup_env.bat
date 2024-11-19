@echo off
title Welcome to Mirchi AI - PP Tools Installations. Please wait while the Web UI launches Automatically.

:: Check if Python 3.8.0 is installed
echo Checking for Python 3.8.0...
py -3.8 --version 2>nul | find "3.8.0" >nul
if %errorlevel% neq 0 (
    echo Python 3.8.0 not found! We will now download and install it automatically.

    :: Download Python 3.8.0 installer (Windows 64-bit version)
    echo Downloading Python 3.8.0 installer...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe -OutFile python-3.8.0-amd64.exe"
    
    :: Check if the download was successful
    if not exist python-3.8.0-amd64.exe (
        echo Error downloading Python 3.8.0 installer. Please check your internet connection and try again.
        pause
        exit /b
    )

    :: Install Python 3.8.0 silently
    echo Installing Python 3.8.0...
    start /wait python-3.8.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

    :: Check if Python 3.8.0 was installed successfully
    py -3.8 --version 2>nul | find "3.8.0" >nul
    if %errorlevel% neq 0 (
        echo Installation failed! Please install Python 3.8.0 manually and rerun the script.
        pause
        exit /b
    )

    :: Clean up installer file
    del python-3.8.0-amd64.exe
    echo Python 3.8.0 installed successfully.
)

:: Create virtual environment using py -3.8
echo Creating virtual environment...
py -3.8 -m venv venv

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install required dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

:: Run the Python script (Assuming it's a script that launches the web UI)
echo Launching the Web UI...
python aipp.py

:: Deactivate virtual environment after the web UI starts
deactivate

pause
