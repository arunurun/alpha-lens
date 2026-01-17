# Indicators module
import pandas as pd
import numpy as np


def add_ema(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """
    Add Exponential Moving Average (EMA) indicator to DataFrame.
    
    Args:
        df: DataFrame with 'Close' column
        period: Period for EMA calculation (default: 20)
    
    Returns:
        DataFrame with 'EMA_{period}' column added
    """
    df = df.copy()
    df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add Relative Strength Index (RSI) indicator to DataFrame.
    
    Args:
        df: DataFrame with 'Close' column
        period: Period for RSI calculation (default: 14)
    
    Returns:
        DataFrame with 'RSI_{period}' column added
    """
    df = df.copy()
    delta = df['Close'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
    
    return df


def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add Average Directional Index (ADX) indicator to DataFrame.
    
    Args:
        df: DataFrame with 'High', 'Low', 'Close' columns
        period: Period for ADX calculation (default: 14)
    
    Returns:
        DataFrame with 'ADX_{period}' column added
    """
    df = df.copy()
    
    # Calculate True Range (TR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate Directional Movement
    plus_dm = df['High'].diff()
    minus_dm = -df['Low'].diff()
    
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # Calculate smoothed TR and DM
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # Calculate ADX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    df[f'ADX_{period}'] = dx.rolling(window=period).mean()
    
    return df


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Volume Weighted Average Price (VWAP) indicator to DataFrame.
    Calculates VWAP on a daily basis.
    
    Args:
        df: DataFrame with 'High', 'Low', 'Close', 'Volume' columns
    
    Returns:
        DataFrame with 'VWAP' column added
    """
    df = df.copy()
    
    # Calculate typical price
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    
    # Calculate VWAP (cumulative)
    df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    return df


def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Add Bollinger Bands indicator to DataFrame.
    
    Args:
        df: DataFrame with 'Close' column
        period: Period for moving average (default: 20)
        std_dev: Number of standard deviations (default: 2.0)
    
    Returns:
        DataFrame with 'BB_Upper', 'BB_Middle', 'BB_Lower' columns added
    """
    df = df.copy()
    
    # Calculate middle band (SMA)
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    
    # Calculate standard deviation
    std = df['Close'].rolling(window=period).std()
    
    # Calculate upper and lower bands
    df['BB_Upper'] = df['BB_Middle'] + (std * std_dev)
    df['BB_Lower'] = df['BB_Middle'] - (std * std_dev)
    
    return df


def add_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """
    Add SuperTrend indicator to DataFrame.
    
    Args:
        df: DataFrame with 'High', 'Low', 'Close' columns
        period: Period for ATR calculation (default: 10)
        multiplier: Multiplier for ATR (default: 3.0)
    
    Returns:
        DataFrame with 'SuperTrend', 'SuperTrend_Direction' columns added
    """
    df = df.copy()
    
    # Calculate ATR (Average True Range)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    # Calculate basic bands
    hl_avg = (df['High'] + df['Low']) / 2
    upper_band_base = hl_avg + (multiplier * atr)
    lower_band_base = hl_avg - (multiplier * atr)
    
    # Initialize arrays for SuperTrend calculation
    supertrend = np.zeros(len(df))
    direction = np.zeros(len(df))
    upper_band = np.zeros(len(df))
    lower_band = np.zeros(len(df))
    
    for i in range(len(df)):
        if i == 0:
            upper_band[i] = upper_band_base.iloc[i]
            lower_band[i] = lower_band_base.iloc[i]
            supertrend[i] = upper_band[i]
            direction[i] = -1
        else:
            # Update upper band
            if upper_band_base.iloc[i] < supertrend[i-1] or df['Close'].iloc[i-1] > supertrend[i-1]:
                upper_band[i] = upper_band_base.iloc[i]
            else:
                upper_band[i] = supertrend[i-1]
            
            # Update lower band
            if lower_band_base.iloc[i] > supertrend[i-1] or df['Close'].iloc[i-1] < supertrend[i-1]:
                lower_band[i] = lower_band_base.iloc[i]
            else:
                lower_band[i] = supertrend[i-1]
            
            # Determine SuperTrend value and direction
            if supertrend[i-1] == upper_band[i-1] and df['Close'].iloc[i] <= upper_band[i]:
                supertrend[i] = upper_band[i]
            elif supertrend[i-1] == upper_band[i-1] and df['Close'].iloc[i] > upper_band[i]:
                supertrend[i] = lower_band[i]
            elif supertrend[i-1] == lower_band[i-1] and df['Close'].iloc[i] >= lower_band[i]:
                supertrend[i] = lower_band[i]
            elif supertrend[i-1] == lower_band[i-1] and df['Close'].iloc[i] < lower_band[i]:
                supertrend[i] = upper_band[i]
            else:
                supertrend[i] = supertrend[i-1]
            
            # Set direction: 1 for uptrend, -1 for downtrend
            if df['Close'].iloc[i] > supertrend[i]:
                direction[i] = 1
            else:
                direction[i] = -1
    
    df['SuperTrend'] = supertrend
    df['SuperTrend_Direction'] = direction
    
    return df
