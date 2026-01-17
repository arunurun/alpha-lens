# Installing Python on Windows

## Step 1: Download Python

1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow "Download Python 3.x.x" button (latest version)
3. The installer will download automatically

## Step 2: Install Python

1. **Run the installer** (python-3.x.x-amd64.exe)
2. **IMPORTANT**: Check the box that says **"Add Python to PATH"** at the bottom
3. Click **"Install Now"**
4. Wait for installation to complete
5. Click **"Close"** when done

## Step 3: Verify Installation

1. **Close and reopen** your terminal/PowerShell/Command Prompt
2. Run this command:
   ```powershell
   python --version
   ```
3. You should see something like: `Python 3.11.x` or `Python 3.12.x`

## Step 4: Install Project Dependencies

Once Python is installed, navigate to the Stocks folder and run:

```powershell
cd C:\Arun\Study\Cursor\Stocks
python -m pip install -r requirements.txt
```

## Step 5: Run the App

```powershell
python -m streamlit run app.py
```

## Troubleshooting

### If "python" still doesn't work after installation:

1. **Restart your computer** (sometimes needed for PATH changes)
2. Try using `py` instead:
   ```powershell
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

### If you forgot to check "Add Python to PATH":

1. Uninstall Python
2. Reinstall Python and **check "Add Python to PATH"** this time
3. Or manually add Python to PATH (more complex)

### Alternative: Use Python from Microsoft Store

If the above doesn't work, you can install Python from Microsoft Store:
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Install"
4. After installation, restart your terminal

## Quick Check Commands

After installation, verify everything works:

```powershell
# Check Python version
python --version

# Check pip (package installer)
python -m pip --version

# Install dependencies
python -m pip install -r requirements.txt

# Run the app
python -m streamlit run app.py
```

## Need Help?

If you're still having issues:
1. Make sure you restarted your terminal after installing Python
2. Try restarting your computer
3. Check that Python is in your PATH by running: `where python`
4. If nothing works, try the Microsoft Store version of Python
