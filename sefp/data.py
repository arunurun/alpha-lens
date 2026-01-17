# Data module
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

# NIFTY 50 stock symbols (Indian stock market)
NIFTY50_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "BAJFINANCE.NS", "LICI.NS",
    "ITC.NS", "SUNPHARMA.NS", "HCLTECH.NS", "AXISBANK.NS", "KOTAKBANK.NS",
    "LT.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "WIPRO.NS", "NESTLEIND.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS",
    "M&M.NS", "TECHM.NS", "ADANIENT.NS", "JSWSTEEL.NS", "TATAMOTORS.NS",
    "ADANIPORTS.NS", "TATASTEEL.NS", "DIVISLAB.NS", "BAJAJFINSV.NS",
    "HINDALCO.NS", "GRASIM.NS", "BRITANNIA.NS", "SBILIFE.NS", "HEROMOTOCO.NS",
    "APOLLOHOSP.NS", "DRREDDY.NS", "COALINDIA.NS", "CIPLA.NS", "EICHERMOT.NS",
    "BPCL.NS", "MARICO.NS", "INDUSINDBK.NS", "ADANIPOWER.NS", "GODREJCP.NS"
]


def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV (Open, High, Low, Close, Volume) data for a stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS" for Indian stocks)
    
    Returns:
        pandas DataFrame with OHLCV data
    
    Raises:
        ValueError: If the fetched data has fewer than 150 rows
    """
    # Calculate date range: at least 1 year of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400)  # Fetch extra days to account for weekends/holidays
    
    # Fetch data using yfinance
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)
    
    # Check if data was fetched successfully
    if df.empty:
        raise ValueError(f"No data available for symbol: {symbol}")
    
    # Validate minimum row count
    if len(df) < 150:
        raise ValueError(
            f"Insufficient data for symbol {symbol}: "
            f"Expected at least 150 rows, got {len(df)} rows. "
            f"This may indicate insufficient trading history or data availability issues."
        )
    
    return df


def fetch_market_context() -> Dict[str, Any]:
    """
    Fetch global market context (NIFTY 50 index) for correlation analysis.
    
    Returns:
        Dictionary with market context information
    """
    try:
        # Fetch NIFTY 50 index data
        nifty_ticker = yf.Ticker("^NSEI")
        nifty_df = nifty_ticker.history(period="5d")
        
        if nifty_df.empty:
            return {
                'nifty_trend': 'Unknown',
                'nifty_change_pct': None,
                'market_sentiment': 'Neutral'
            }
        
        latest = nifty_df.iloc[-1]
        previous = nifty_df.iloc[-2] if len(nifty_df) > 1 else latest
        
        nifty_change = ((latest['Close'] - previous['Close']) / previous['Close']) * 100
        
        # Determine trend
        if nifty_change > 0.5:
            nifty_trend = 'Bullish'
            market_sentiment = 'Positive'
        elif nifty_change < -0.5:
            nifty_trend = 'Bearish'
            market_sentiment = 'Negative'
        else:
            nifty_trend = 'Neutral'
            market_sentiment = 'Neutral'
        
        return {
            'nifty_trend': nifty_trend,
            'nifty_change_pct': round(nifty_change, 2),
            'nifty_level': round(float(latest['Close']), 2),
            'market_sentiment': market_sentiment
        }
    except Exception as e:
        return {
            'nifty_trend': 'Unknown',
            'nifty_change_pct': None,
            'market_sentiment': 'Neutral',
            'error': str(e)
        }
