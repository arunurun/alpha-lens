@echo off
echo Starting Alpha Lens Servers...
echo.
cd /d "%~dp0"
echo Starting backend on http://localhost:8000 ...
start "Alpha Lens Backend" cmd /k "python -m uvicorn backend:app --reload --port 8000"
timeout /t 2 >nul
echo Starting Streamlit app on http://localhost:8501 ...
start "Alpha Lens App" cmd /k "python -m streamlit run app.py"
pause
