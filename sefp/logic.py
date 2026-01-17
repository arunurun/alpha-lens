# Logic module
import pandas as pd
from typing import Dict, Any


def analyze_sefp(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze stock data using simplified SEFP Phase 3 logic.
    
    Rules:
    - Trend valid if SuperTrend is green AND ADX > 20 AND Close > VWAP
    - RSI 45–60 → accumulation (bullish)
    - RSI > 70 or < 30 → exhaustion
    - Volume confirmed if latest volume > 1.5 × 20-day average
    
    Args:
        df: DataFrame with required indicator columns:
            - SuperTrend
            - SuperTrend_Direction
            - ADX_14
            - VWAP
            - Close
            - RSI_14
            - Volume
    
    Returns:
        Dictionary with:
        - trend_valid (bool): Whether trend conditions are met
        - momentum (str): 'bullish', 'neutral', or 'exhausted'
        - volume_confirmed (bool): Whether volume is confirmed
        - notes (list): List of short descriptive strings
    """
    if df.empty:
        return {
            'trend_valid': False,
            'momentum': 'neutral',
            'volume_confirmed': False,
            'notes': ['No data available']
        }
    
    # Get the latest row (most recent data)
    latest = df.iloc[-1]
    notes = []
    
    # Check required columns exist
    required_cols = ['SuperTrend', 'SuperTrend_Direction', 'ADX_14', 'VWAP', 'Close', 'RSI_14', 'Volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {
            'trend_valid': False,
            'momentum': 'neutral',
            'volume_confirmed': False,
            'notes': [f'Missing required columns: {", ".join(missing_cols)}']
        }
    
    # 1. Check trend validity
    # SuperTrend is green if SuperTrend_Direction == 1
    supertrend_green = latest['SuperTrend_Direction'] == 1
    adx_above_threshold = latest['ADX_14'] > 20
    close_above_vwap = latest['Close'] > latest['VWAP']
    
    trend_valid = supertrend_green and adx_above_threshold and close_above_vwap
    
    if not supertrend_green:
        notes.append('SuperTrend is red (downtrend)')
    if not adx_above_threshold:
        notes.append(f'ADX below 20 (weak trend): {latest["ADX_14"]:.2f}')
    if not close_above_vwap:
        notes.append('Close below VWAP')
    if trend_valid:
        notes.append('Trend is valid')
    
    # 2. Determine momentum based on RSI
    rsi = latest['RSI_14']
    if pd.isna(rsi):
        momentum = 'neutral'
        notes.append('RSI data unavailable')
    elif 45 <= rsi <= 60:
        momentum = 'bullish'
        notes.append(f'RSI in accumulation zone: {rsi:.2f}')
    elif rsi > 70 or rsi < 30:
        momentum = 'exhausted'
        if rsi > 70:
            notes.append(f'RSI overbought (exhaustion): {rsi:.2f}')
        else:
            notes.append(f'RSI oversold (exhaustion): {rsi:.2f}')
    else:
        momentum = 'neutral'
        notes.append(f'RSI neutral: {rsi:.2f}')
    
    # 3. Check volume confirmation
    latest_volume = latest['Volume']
    if len(df) >= 20:
        avg_volume_20d = df['Volume'].tail(20).mean()
        volume_confirmed = latest_volume > (1.5 * avg_volume_20d)
        
        if volume_confirmed:
            notes.append(f'Volume confirmed: {latest_volume:,.0f} > 1.5x avg ({avg_volume_20d:,.0f})')
        else:
            notes.append(f'Volume not confirmed: {latest_volume:,.0f} <= 1.5x avg ({avg_volume_20d:,.0f})')
    else:
        volume_confirmed = False
        notes.append('Insufficient data for volume confirmation (need 20 days)')
    
    return {
        'trend_valid': trend_valid,
        'momentum': momentum,
        'volume_confirmed': volume_confirmed,
        'notes': notes
    }