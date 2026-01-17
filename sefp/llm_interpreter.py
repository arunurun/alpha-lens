# LLM Interpreter module
import pandas as pd
import numpy as np
import json
from typing import Dict, Any, Optional


def format_verdict_for_llm(
    stock_symbol: str,
    analysis: Dict[str, Any],
    verdict: Dict[str, Any],
    df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Format verdict data for LLM interpretation.
    
    Args:
        stock_symbol: Stock symbol (e.g., "RELIANCE.NS")
        analysis: Dictionary from analyze_sefp()
        verdict: Dictionary from calculate_verdict()
        df: DataFrame with indicator columns
    
    Returns:
        Dictionary formatted for LLM interpretation
    """
    if df.empty:
        return {
            'stock': stock_symbol.replace('.NS', ''),
            'insufficient_data': True
        }
    
    latest = df.iloc[-1]
    
    # Determine market regime based on SuperTrend (convert to native Python bool/int)
    supertrend_dir = latest.get('SuperTrend_Direction', 0)
    if pd.notna(supertrend_dir):
        supertrend_dir = int(supertrend_dir)
    market_regime = "Bull" if supertrend_dir == 1 else "Bear"
    
    # Determine price vs VWAP (convert to native Python types)
    close_price = float(latest.get('Close', 0)) if pd.notna(latest.get('Close', 0)) else 0
    vwap_price = float(latest.get('VWAP', 0)) if pd.notna(latest.get('VWAP', 0)) else 0
    price_vs_vwap = "above" if close_price > vwap_price else "below"
    
    # Get RSI and ADX values
    rsi = latest.get('RSI_14', None)
    adx = latest.get('ADX_14', None)
    
    # Format RSI and ADX (handle NaN and convert to native Python float)
    rsi_value = round(float(rsi), 1) if pd.notna(rsi) else None
    adx_value = round(float(adx), 1) if pd.notna(adx) else None
    
    # Determine Wyckoff phase based on momentum and RSI
    momentum = analysis.get('momentum', 'neutral')
    if momentum == 'bullish' and rsi_value and 45 <= rsi_value <= 60:
        wyckoff_phase = "Markup"
    elif momentum == 'exhausted' and rsi_value and rsi_value > 70:
        wyckoff_phase = "Distribution"
    elif momentum == 'exhausted' and rsi_value and rsi_value < 30:
        wyckoff_phase = "Markdown"
    else:
        wyckoff_phase = "Accumulation"
    
    # Calculate delivery deviation (simplified - using volume confirmation)
    volume_confirmed = analysis.get('volume_confirmed', False)
    if volume_confirmed and len(df) >= 20:
        latest_volume = latest.get('Volume', 0)
        avg_volume = df['Volume'].tail(20).mean()
        if avg_volume > 0:
            deviation = ((latest_volume - avg_volume) / avg_volume) * 100
            delivery_deviation = f"{deviation:+.0f}%"
        else:
            delivery_deviation = "N/A"
    else:
        delivery_deviation = "N/A"
    
    # Convert to JSON-serializable types
    return {
        'stock': stock_symbol.replace('.NS', ''),
        'market_regime': market_regime,
        'trend_valid': bool(analysis.get('trend_valid', False)),
        'adx': float(adx_value) if adx_value is not None else None,
        'rsi': float(rsi_value) if rsi_value is not None else None,
        'price_vs_vwap': price_vs_vwap,
        'volume_confirmed': bool(analysis.get('volume_confirmed', False)),
        'wyckoff_phase': wyckoff_phase,
        'delivery_deviation': delivery_deviation,
        'score': int(verdict.get('score', 0)),
        'action': str(verdict.get('action', 'AVOID'))
    }


def create_llm_request(
    stock_symbol: str,
    analysis: Dict[str, Any],
    verdict: Dict[str, Any],
    df: pd.DataFrame,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create LLM API request payload for verdict interpretation.
    
    Args:
        stock_symbol: Stock symbol
        analysis: Dictionary from analyze_sefp()
        verdict: Dictionary from calculate_verdict()
        df: DataFrame with indicator columns
        model: LLM model name (default: "gpt-4o-mini")
        api_key: Optional API key (if None, returns request without calling API)
    
    Returns:
        Dictionary with API request payload
    """
    verdict_data = format_verdict_for_llm(stock_symbol, analysis, verdict, df)
    
    system_prompt = """You are an Equity Forensics Interpreter operating under the Supreme Equity Forensic Protocol (SEFP). You ONLY interpret the provided facts and produce a structured verdict. DO NOT compute indicators or scores. DO NOT infer missing information. DO NOT override the score or action. If data is missing, output 'INSUFFICIENT DATA — NO VERDICT'. Respond in concise, professional institutional style, ≤5 lines, with no emojis or storytelling. Output EXACTLY in this format:

Stock:
Forensic Verdict:
Trend Assessment:
Action:
Risk Note:"""
    
    # Convert to JSON-serializable types (handle numpy/pandas types)
    def make_json_serializable(obj):
        """Convert numpy/pandas types to native Python types"""
        if isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        elif isinstance(obj, (int, np.integer)):
            return int(obj)
        elif isinstance(obj, (float, np.floating)):
            return float(obj) if not pd.isna(obj) else None
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    json_safe_data = {k: make_json_serializable(v) for k, v in verdict_data.items()}
    
    user_prompt = f"Interpret the following stock analysis:\n```json\n{json.dumps(json_safe_data, indent=2)}\n```"
    
    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 120
    }
    
    return request_payload


def create_user_friendly_interpretation(
    stock_symbol: str,
    analysis: Dict[str, Any],
    verdict: Dict[str, Any],
    df: pd.DataFrame,
    market_context: Optional[Dict[str, Any]] = None,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Create a user-friendly LLM interpretation with global market context.
    
    Args:
        stock_symbol: Stock symbol
        analysis: Dictionary from analyze_sefp()
        verdict: Dictionary from calculate_verdict()
        df: DataFrame with indicator columns
        market_context: Optional market context dictionary
        model: LLM model name
    
    Returns:
        Dictionary with user-friendly interpretation request
    """
    verdict_data = format_verdict_for_llm(stock_symbol, analysis, verdict, df)
    latest = df.iloc[-1]
    
    # Build context summary
    context_summary = {
        'stock_name': stock_symbol.replace('.NS', ''),
        'current_price': f"₹{float(latest['Close']):.2f}" if pd.notna(latest.get('Close')) else "N/A",
        'score': verdict_data['score'],
        'recommendation': verdict_data['action'],
        'trend_status': 'Uptrend' if verdict_data['trend_valid'] else 'Downtrend or Weak Trend',
        'rsi_level': verdict_data['rsi'],
        'rsi_interpretation': (
            'Oversold (potential buying opportunity)' if verdict_data['rsi'] and verdict_data['rsi'] < 30 else
            'Overbought (potential selling opportunity)' if verdict_data['rsi'] and verdict_data['rsi'] > 70 else
            'Neutral zone'
        ),
        'volume_status': 'High volume (strong interest)' if verdict_data['volume_confirmed'] else 'Normal volume',
        'price_position': f"Trading {'above' if verdict_data['price_vs_vwap'] == 'above' else 'below'} average price (VWAP)",
        'market_regime': verdict_data['market_regime']
    }
    
    # Add market context if available
    market_info = ""
    if market_context:
        market_info = f"""
Global Market Context:
- NIFTY 50 Index Trend: {market_context.get('nifty_trend', 'Unknown')}
- Market Change: {market_context.get('nifty_change_pct', 'N/A')}%
- Overall Market Sentiment: {market_context.get('market_sentiment', 'Neutral')}
"""
    
    system_prompt = """You are a friendly financial advisor explaining stock analysis in simple, easy-to-understand language. 
Your goal is to help regular investors understand:
1. What the analysis means in plain English
2. Why the recommendation (BUY/WAIT/AVOID) was made
3. How global market conditions relate to this stock
4. What key factors influenced the decision

Be conversational, clear, and avoid jargon. Use analogies when helpful. Keep it under 200 words.
Structure your response with:
- A brief summary of the stock's current situation
- Explanation of the recommendation and why
- Connection to broader market trends (if provided)
- Key factors to watch"""
    
    user_prompt = f"""Please explain this stock analysis in simple, easy-to-understand language:

Stock: {context_summary['stock_name']}
Current Price: {context_summary['current_price']}
Recommendation: {context_summary['recommendation']} (Score: {context_summary['score']}/100)

Key Findings:
- Trend: {context_summary['trend_status']}
- RSI Level: {context_summary['rsi_level']} ({context_summary['rsi_interpretation']})
- Volume: {context_summary['volume_status']}
- Price Position: {context_summary['price_position']}
- Market Regime: {context_summary['market_regime']} market
{market_info}

Technical Details:
{json.dumps(verdict_data, indent=2)}

Please explain:
1. What does this analysis tell us about {context_summary['stock_name']}?
2. Why is the recommendation "{context_summary['recommendation']}"?
3. How do global market conditions (if provided) relate to this stock?
4. What should an investor watch for?"""
    
    # Convert to JSON-serializable types
    def make_json_serializable(obj):
        """Convert numpy/pandas types to native Python types"""
        if isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        elif isinstance(obj, (int, np.integer)):
            return int(obj)
        elif isinstance(obj, (float, np.floating)):
            return float(obj) if not pd.isna(obj) else None
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    json_safe_data = {k: make_json_serializable(v) for k, v in verdict_data.items()}
    
    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    return request_payload
