from typing import Any, Dict, List, Optional

import os
import requests
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="Alpha Lens Chat Backend")


class ChatRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token or access token")
    messages: List[Dict[str, Any]]
    model: str = "gpt-4o-mini"


class ChatResponse(BaseModel):
    content: str


def verify_google_token(id_token: str) -> Dict[str, Any]:
    # Try ID token validation first
    tokeninfo_url = "https://oauth2.googleapis.com/tokeninfo"
    resp = requests.get(tokeninfo_url, params={"id_token": id_token}, timeout=10)
    if resp.status_code != 200:
        # Fallback: try as access token
        resp = requests.get(tokeninfo_url, params={"access_token": id_token}, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    data = resp.json()
    expected_aud = os.getenv("GOOGLE_CLIENT_ID")
    if expected_aud and data.get("aud") and data.get("aud") != expected_aud:
        raise HTTPException(status_code=401, detail="Token audience mismatch")
    return data


def call_openai(messages: List[Dict[str, Any]], model: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300,
    }
    retries = 3
    backoff = 2
    for attempt in range(retries + 1):
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 429 and attempt < retries:
            time.sleep(backoff)
            backoff *= 2
            continue
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    raise HTTPException(status_code=429, detail="Rate limit reached. Please retry.")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    verify_google_token(req.id_token)
    content = call_openai(req.messages, req.model)
    return ChatResponse(content=content)
