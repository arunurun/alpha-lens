@echo off
echo Installing Alpha Lens dependencies...
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Python command failed. Trying python3...
    python3 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Python3 command failed. Trying py...
        py -m pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo ERROR: Could not find Python installation.
            echo Please install Python 3.10+ from https://www.python.org/downloads/
            echo Make sure to check "Add Python to PATH" during installation.
            pause
            exit /b 1
        )
    )
)
echo.
echo Dependencies installed successfully!
echo.
echo To run the app, use: python -m streamlit run app.py
echo Or double-click run_app.bat
pause
