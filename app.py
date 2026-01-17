import streamlit as st
import pandas as pd
import json
import requests
import os
import html
from pathlib import Path
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
            st.info("💡 **Note:** This is a formatted request for LLM interpretation. To get the actual explanation, you'll need to call your LLM API with the request shown below.")
            
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

# --- Chat Assistant ---
def load_sefp_rules() -> str:
    rules_path = Path(__file__).with_name("rules.md")
    try:
        return rules_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def get_google_oauth():
    try:
        from authlib.integrations.requests_client import OAuth2Session
    except ModuleNotFoundError:
        st.error("Authlib is not installed. Run: python -m pip install authlib")
        raise
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    return OAuth2Session(
        client_id=client_id,
        client_secret=client_secret,
        scope="openid email profile",
        redirect_uri=redirect_uri,
    )


def ensure_google_login() -> bool:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    if not client_id or not client_secret:
        st.error("Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment.")
        return False

    params = st.query_params
    if "code" in params:
        raw_code = params.get("code")
        raw_state = params.get("state")
        code = raw_code[0] if isinstance(raw_code, list) else raw_code
        state = raw_state[0] if isinstance(raw_state, list) else raw_state
        expected_state = st.session_state.get("oauth_state")
        if state and expected_state and state != expected_state:
            st.error("OAuth state mismatch. Please try signing in again.")
            return False
        oauth = get_google_oauth()
        try:
            token = oauth.fetch_token(
                "https://oauth2.googleapis.com/token",
                code=code,
                redirect_uri=redirect_uri,
            )
        except Exception as e:
            st.error("Google login failed. Please try again.")
            st.info(
                "Common causes: redirect URI mismatch or reused login link. "
                f"Current redirect URI: {redirect_uri}"
            )
            st.query_params.clear()
            return False
        userinfo = oauth.get("https://openidconnect.googleapis.com/v1/userinfo").json()
        st.session_state["user"] = userinfo
        st.session_state["oauth_token"] = token
        st.query_params.clear()
        st.rerun()

    if "user" not in st.session_state:
        oauth = get_google_oauth()
        auth_url, state = oauth.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            access_type="offline",
            prompt="select_account",
        )
        st.session_state["oauth_state"] = state
        st.info("Sign in with Google to use the chat assistant.")
        st.markdown(
            f'<a href="{auth_url}" target="_self">Sign in with Google</a>',
            unsafe_allow_html=True,
        )
        return False

    user = st.session_state.get("user", {})
    st.success(f"Signed in as {user.get('email', 'Google user')}")
    if st.button("Sign out"):
        st.session_state.pop("user", None)
        st.session_state.pop("oauth_token", None)
        st.session_state.pop("oauth_state", None)
        st.session_state.pop("chat_messages", None)
        st.rerun()
    return True

def build_chat_messages(user_message: str) -> list:
    rules = load_sefp_rules()
    context = st.session_state.get("last_context")
    context_summary = ""
    if context:
        context_summary = json.dumps(
            {
                "symbol": context.get("symbol"),
                "analysis": context.get("analysis"),
                "verdict": context.get("verdict"),
                "market_context": context.get("market_context"),
                "llm_data": context.get("llm_data"),
            },
            default=str,
            indent=2,
        )
    system_prompt = (
        "You are an SEFP Assistant. Use ONLY the provided rules and context. "
        "If the user asks for data not present, say you need more data. "
        "Keep responses concise and practical.\n\nSEFP Rules:\n"
        + rules
        + "\n\nContext (if any):\n"
        + (context_summary or "No analysis context available yet.")
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def call_chat_llm(id_token: str, messages: list, model: str = "gpt-4o-mini") -> str:
    # Streamlit Cloud: call OpenAI directly using server-side secret
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY. Set it in Streamlit secrets.")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 429:
        raise requests.HTTPError("Rate limit hit. Please wait a bit and try again.", response=response)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


st.markdown("---")
st.markdown(
    """
<style>
[data-testid="stChatInput"] {
  margin-top: 8px;
}
[data-testid="stChatMessage"] {
  background: transparent;
  border: none;
  padding: 0;
  margin-bottom: 12px;
}
[data-testid="stChatInput"] textarea {
  border-radius: 14px;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #0f172a;
  color: #ffffff;
  padding: 14px 18px;
  border-radius: 14px;
  margin-bottom: 14px;
}
.chat-subtitle {
  color: #cbd5e1;
  font-size: 0.9rem;
}
.chat-shell {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 8px;
}
.bubble {
  max-width: 80%;
  padding: 12px 14px;
  border-radius: 14px;
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 0.95rem;
}
.bubble.user {
  margin-left: auto;
  background: #0f172a;
  color: #ffffff;
  border-bottom-right-radius: 4px;
}
.bubble.assistant {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}
.bubble-meta {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 4px;
}
.status-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  background: #e2e8f0;
  color: #0f172a;
}
</style>
<div class="chat-header">
  <div>
    <div style="font-size: 1.1rem; font-weight: 600;">Alpha Lens Assistant</div>
    <div class="chat-subtitle">Ask about the latest analysis in plain language</div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []
if "last_chat_ts" not in st.session_state:
    st.session_state["last_chat_ts"] = 0.0

is_logged_in = ensure_google_login()
oauth_token = st.session_state.get("oauth_token", {})
google_id_token = oauth_token.get("id_token") or oauth_token.get("access_token")

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

if not st.session_state["chat_messages"]:
    st.markdown(
        """
<div class="bubble assistant">
  <div class="bubble-meta">Alpha Lens Assistant</div>
  Ask me anything about the latest analysis. Try one of these:
  <ul>
    <li>Summarize the verdict in 3 bullets</li>
    <li>Why is the recommendation WAIT?</li>
    <li>What should I watch next?</li>
  </ul>
</div>
        """,
        unsafe_allow_html=True,
    )

for msg in st.session_state["chat_messages"]:
    role = "assistant" if msg["role"] != "user" else "user"
    label = "Alpha Lens Assistant" if role == "assistant" else "You"
    content = html.escape(msg["content"])
    st.markdown(
        f'<div class="bubble {role}"><div class="bubble-meta">{label}</div>{content}</div>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

quick_prompts = [
    "Summarize the verdict in 3 bullets",
    "Why is the recommendation WAIT?",
    "What should I watch next?",
    "Explain in very simple terms",
]
cols = st.columns(len(quick_prompts))
for idx, prompt in enumerate(quick_prompts):
    if cols[idx].button(prompt, use_container_width=True):
        st.session_state["pending_prompt"] = prompt

user_input = st.chat_input("Ask the assistant about this stock...")
if not user_input and st.session_state.get("pending_prompt"):
    user_input = st.session_state.pop("pending_prompt")
if user_input:
    import time
    now = time.time()
    if now - st.session_state["last_chat_ts"] < 10:
        st.warning("Please wait a few seconds between messages to avoid rate limits.")
        user_input = None
    else:
        st.session_state["last_chat_ts"] = now

if user_input:
    st.session_state["chat_messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    if not is_logged_in:
        with st.chat_message("assistant"):
            st.write("Please sign in with Google to enable chat responses.")
    else:
        try:
            messages = build_chat_messages(user_input)
            if not google_id_token:
                raise ValueError("Missing Google token. Please sign in again.")
            response_text = call_chat_llm(google_id_token, messages)
            st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.write(response_text)
        except requests.HTTPError as e:
            with st.chat_message("assistant"):
                if e.response is not None and e.response.status_code == 429:
                    st.write("Rate limit reached. Please wait 30–60 seconds and try again.")
                else:
                    st.write(f"Error contacting LLM: {str(e)}")
        except Exception as e:
            with st.chat_message("assistant"):
                st.write(f"Error contacting LLM: {str(e)}")
