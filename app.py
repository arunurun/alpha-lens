import streamlit as st
import pandas as pd
import json
import requests
import os
import html
from sefp.data import fetch_stock_data, NIFTY50_SYMBOLS, fetch_market_context
from sefp.indicators import (
    add_ema, add_rsi, add_adx, add_vwap,
    add_bollinger_bands, add_supertrend
)
from sefp.logic import analyze_sefp
from sefp.verdict import calculate_verdict
from sefp.llm_interpreter import format_verdict_for_llm, create_user_friendly_interpretation

st.title("Alpha Lens")

# Disclaimer
st.warning("⚠️ Educational use only. Not financial advice.")

# Stock selection
st.subheader("Select Stock")
selected_symbol = st.selectbox(
    "Choose a NIFTY 50 stock:",
    options=NIFTY50_SYMBOLS,
    format_func=lambda x: x.replace(".NS", "").replace("_", " ")
)

# Analyze button
if st.button("Analyze", type="primary"):
    with st.spinner("Fetching data and analyzing..."):
        try:
            # Fetch data
            df = fetch_stock_data(selected_symbol)
            
            # Add all indicators
            df = add_ema(df)
            df = add_rsi(df)
            df = add_adx(df)
            df = add_vwap(df)
            df = add_bollinger_bands(df)
            df = add_supertrend(df)
            
            # Fetch market context
            market_context = fetch_market_context()
            
            # Run SEFP logic
            analysis = analyze_sefp(df)
            
            # Calculate verdict
            verdict = calculate_verdict(analysis, df)
            # Store context for chat
            st.session_state["last_context"] = {
                "symbol": selected_symbol,
                "analysis": analysis,
                "verdict": verdict,
                "market_context": market_context,
                "llm_data": format_verdict_for_llm(selected_symbol, analysis, verdict, df),
            }
            
            # Display results
            st.success("Analysis Complete!")
            
            # Score and Action
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{verdict['score']}/100")
            with col2:
                action_color = {
                    'BUY': '🟢',
                    'WAIT': '🟡',
                    'AVOID': '🔴'
                }
                st.metric("Action", f"{action_color.get(verdict['action'], '')} {verdict['action']}")
            
            # User-Friendly Interpretation
            st.subheader("Investor-Friendly Summary")
            
            
            # Create user-friendly interpretation request
            user_friendly_request = create_user_friendly_interpretation(
                selected_symbol, analysis, verdict, df, market_context
            )
            
            # Display market context if available
            if market_context and 'nifty_trend' in market_context:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("NIFTY Trend", market_context.get('nifty_trend', 'Unknown'))
                with col2:
                    change = market_context.get('nifty_change_pct', 0)
                    if change:
                        st.metric("NIFTY Change", f"{change:+.2f}%")
                    else:
                        st.metric("NIFTY Change", "N/A")
                with col3:
                    st.metric("Market Sentiment", market_context.get('market_sentiment', 'Neutral'))
            
            # LLM request is generated but not displayed in the UI
            
            # Plain-language reasoning
            st.subheader("Plain-Language Summary")

            def simplify_reasoning(text: str) -> str:
                replacements = {
                    "Weak conditions with score": "Overall signals are weak (score",
                    "Moderate conditions with score": "Signals are mixed (score",
                    "Strong buy signal with score": "Signals are strong (score",
                    "Key factors:": "Main reasons:",
                    "Trend valid": "Trend looks supportive",
                    "Volume confirmed": "Higher-than-usual trading activity",
                    "RSI in accumulation zone": "Momentum is steady and building",
                    "Price above VWAP": "Price is trading above its recent average",
                    "Strong trend strength, ADX > 25": "Trend momentum is strong",
                    "Recommendation: Consider entering position with proper risk management.": "Suggestion: You may consider an entry, with cautious risk control.",
                    "Recommendation: Monitor for improved conditions before entry.": "Suggestion: Wait and watch for clearer signals.",
                    "Recommendation: Avoid entry until conditions improve.": "Suggestion: Hold off for now until conditions improve.",
                }
                for old, new in replacements.items():
                    if old in text:
                        text = text.replace(old, new)
                return text

            reasoning_lines = verdict["reasoning"].split(". ")
            for line in reasoning_lines:
                if line.strip():
                    st.write(f"• {simplify_reasoning(line.strip())}")
            
            # Analysis details and LLM data are intentionally hidden from the UI
        
        except ValueError as e:
            st.error(f"Data Error: {str(e)}")
        except KeyError as e:
            st.error(f"Missing data column: {str(e)}. Please ensure all indicators are calculated correctly.")
        except AttributeError as e:
            st.error(f"Data structure error: {str(e)}. Please check the stock symbol and try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.exception(e)

# Footer disclaimer
st.markdown("---")
st.caption("⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.")

