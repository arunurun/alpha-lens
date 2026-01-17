# Testing Guide

## Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

## Step 1: Set Up Virtual Environment (Recommended)

```bash
# Navigate to the Stocks directory
cd Stocks

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit (for the web app)
- yfinance (for stock data)
- pandas (for data manipulation)
- numpy (for numerical calculations)

## Step 3: Run the Streamlit App

```bash
streamlit run app.py
```

The app will:
- Start a local web server
- Open automatically in your browser (usually at `http://localhost:8501`)
- Display the Alpha Lens interface

## Step 4: Test the App

1. **Select a Stock**: Choose any NIFTY 50 stock from the dropdown
2. **Click "Analyze"**: The app will:
   - Fetch stock data (may take a few seconds)
   - Calculate all indicators
   - Run SEFP analysis
   - Display score, action, and reasoning

3. **View Details**: Expand "View Analysis Details" to see:
   - Full analysis results
   - Latest indicator values
   - LLM interpretation data
   - LLM API request format

## Step 5: Test Individual Modules (Optional)

You can test individual modules using Python:

### Test Data Fetching
```python
from sefp.data import fetch_stock_data, NIFTY50_SYMBOLS

# Test fetching data
df = fetch_stock_data("RELIANCE.NS")
print(f"Data shape: {df.shape}")
print(df.head())
```

### Test Indicators
```python
from sefp.data import fetch_stock_data
from sefp.indicators import add_ema, add_rsi, add_adx, add_vwap, add_bollinger_bands, add_supertrend

# Fetch data
df = fetch_stock_data("TCS.NS")

# Add indicators
df = add_ema(df)
df = add_rsi(df)
df = add_adx(df)
df = add_vwap(df)
df = add_bollinger_bands(df)
df = add_supertrend(df)

# Check results
print(df[['Close', 'EMA_20', 'RSI_14', 'ADX_14', 'VWAP', 'SuperTrend']].tail())
```

### Test Logic and Verdict
```python
from sefp.data import fetch_stock_data
from sefp.indicators import add_ema, add_rsi, add_adx, add_vwap, add_bollinger_bands, add_supertrend
from sefp.logic import analyze_sefp
from sefp.verdict import calculate_verdict

# Full pipeline
df = fetch_stock_data("HDFCBANK.NS")
df = add_ema(df)
df = add_rsi(df)
df = add_adx(df)
df = add_vwap(df)
df = add_bollinger_bands(df)
df = add_supertrend(df)

analysis = analyze_sefp(df)
verdict = calculate_verdict(analysis, df)

print("Analysis:", analysis)
print("Verdict:", verdict)
```

### Test LLM Interpreter
```python
from sefp.data import fetch_stock_data
from sefp.indicators import add_ema, add_rsi, add_adx, add_vwap, add_bollinger_bands, add_supertrend
from sefp.logic import analyze_sefp
from sefp.verdict import calculate_verdict
from sefp.llm_interpreter import format_verdict_for_llm, create_llm_request

# Full pipeline
df = fetch_stock_data("INFY.NS")
df = add_ema(df)
df = add_rsi(df)
df = add_adx(df)
df = add_vwap(df)
df = add_bollinger_bands(df)
df = add_supertrend(df)

analysis = analyze_sefp(df)
verdict = calculate_verdict(analysis, df)

# Format for LLM
llm_data = format_verdict_for_llm("INFY.NS", analysis, verdict, df)
llm_request = create_llm_request("INFY.NS", analysis, verdict, df)

print("LLM Data:", llm_data)
print("\nLLM Request:", llm_request)
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Make sure you're in the `Stocks` directory and have activated the virtual environment.

### Issue: yfinance connection errors
**Solution**: 
- Check your internet connection
- Some stock symbols might not be available - try a different NIFTY 50 stock
- Wait a few seconds and try again (rate limiting)

### Issue: Streamlit not found
**Solution**: 
```bash
pip install streamlit
```

### Issue: Port already in use
**Solution**: 
```bash
streamlit run app.py --server.port 8502
```

## Expected Behavior

- **Data Fetching**: Should take 2-5 seconds per stock
- **Analysis**: Should complete in < 1 second after data is fetched
- **Score Range**: 0-100
- **Actions**: BUY (75-100), WAIT (45-74), AVOID (0-44)

## Notes

- First run may be slower as packages are loaded
- Stock data is fetched from Yahoo Finance (requires internet)
- All calculations are done locally (no external API calls for analysis)
- LLM request is formatted but not sent automatically (you need to integrate with your LLM API)
