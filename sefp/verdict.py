# Verdict module
import pandas as pd
from typing import Dict, Any


def calculate_verdict(analysis: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate SEFP Phase 5 scoring and verdict based on analysis results.
    
    Scoring:
    - Trend valid → +30
    - Volume confirmed → +20
    - RSI between 45–60 → +20
    - Price > VWAP → +15
    - ADX > 25 → +15
    
    Map scores:
    - 75–100 → BUY
    - 45–74 → WAIT
    - 0–44 → AVOID
    
    Args:
        analysis: Dictionary from analyze_sefp() containing:
            - trend_valid (bool)
            - momentum (str)
            - volume_confirmed (bool)
            - notes (list)
        df: DataFrame with indicator columns (ADX_14, VWAP, Close, RSI_14)
    
    Returns:
        Dictionary with:
        - score (int): Total score (0-100)
        - action (str): 'BUY', 'WAIT', or 'AVOID'
        - reasoning (str): 2-3 line explanation
    """
    if df.empty:
        return {
            'score': 0,
            'action': 'AVOID',
            'reasoning': 'No data available for analysis. Cannot provide a verdict.'
        }
    
    # Get latest values
    latest = df.iloc[-1]
    score = 0
    score_details = []
    
    # Check required columns
    required_cols = ['ADX_14', 'VWAP', 'Close', 'RSI_14']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {
            'score': 0,
            'action': 'AVOID',
            'reasoning': f'Missing required indicator data: {", ".join(missing_cols)}. Cannot calculate score.'
        }
    
    # 1. Trend valid → +30
    if analysis.get('trend_valid', False):
        score += 30
        score_details.append('Trend valid (+30)')
    
    # 2. Volume confirmed → +20
    if analysis.get('volume_confirmed', False):
        score += 20
        score_details.append('Volume confirmed (+20)')
    
    # 3. RSI between 45–60 → +20
    rsi = latest['RSI_14']
    if not pd.isna(rsi) and 45 <= rsi <= 60:
        score += 20
        score_details.append(f'RSI in accumulation zone (+20)')
    
    # 4. Price > VWAP → +15
    if latest['Close'] > latest['VWAP']:
        score += 15
        score_details.append('Price above VWAP (+15)')
    
    # 5. ADX > 25 → +15
    adx = latest['ADX_14']
    if not pd.isna(adx) and adx > 25:
        score += 15
        score_details.append(f'Strong trend strength, ADX > 25 (+15)')
    
    # Determine action based on score
    if score >= 75:
        action = 'BUY'
    elif score >= 45:
        action = 'WAIT'
    else:
        action = 'AVOID'
    
    # Build reasoning (2-3 lines)
    reasoning_parts = []
    
    # First line: Overall assessment
    if action == 'BUY':
        reasoning_parts.append(f"Strong buy signal with score of {score}/100.")
    elif action == 'WAIT':
        reasoning_parts.append(f"Moderate conditions with score of {score}/100.")
    else:
        reasoning_parts.append(f"Weak conditions with score of {score}/100.")
    
    # Second line: Key positive factors
    if score_details:
        key_factors = ', '.join(score_details[:2])  # Take first 2 factors
        reasoning_parts.append(f"Key factors: {key_factors}.")
    else:
        reasoning_parts.append("No positive scoring factors identified.")
    
    # Third line: Action recommendation
    if action == 'BUY':
        reasoning_parts.append("Recommendation: Consider entering position with proper risk management.")
    elif action == 'WAIT':
        reasoning_parts.append("Recommendation: Monitor for improved conditions before entry.")
    else:
        reasoning_parts.append("Recommendation: Avoid entry until conditions improve.")
    
    reasoning = ' '.join(reasoning_parts)
    
    return {
        'score': score,
        'action': action,
        'reasoning': reasoning
    }