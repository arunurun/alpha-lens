@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Trying python3...
    python3 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Trying py...
        py -m pip install -r requirements.txt
    )
)
echo.
echo Starting Streamlit app...
python -m streamlit run app.py
if errorlevel 1 (
    echo Trying python3...
    python3 -m streamlit run app.py
    if errorlevel 1 (
        echo Trying py...
        py -m streamlit run app.py
    )
)
pause
