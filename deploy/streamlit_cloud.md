## Streamlit Community Cloud Deployment (Free, No Card)

This option hosts the Streamlit app directly. The chat calls OpenAI from the Streamlit server using secrets.

### 1) Push code to GitHub
```bash
git init
git add .
git commit -m "alpha lens"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

### 2) Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io/
2. Connect your GitHub repo
3. Select:
   - **Repository:** your repo
   - **Branch:** main
   - **Main file path:** `app.py`
4. Click **Deploy**

### 3) Add Secrets
In Streamlit Cloud, open **App Settings → Secrets** and add:
```
OPENAI_API_KEY="your_openai_key"
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="https://<your-app>.streamlit.app"
```

### 4) Update Google OAuth Redirect URI
In Google Cloud Console, set the **Authorized redirect URI** to:
```
https://<your-app>.streamlit.app
```

### 5) Done
Open your app URL:
```
https://<your-app>.streamlit.app
```

### Notes
- No backend is required for this option.
- Your OpenAI key remains server-side (in Streamlit secrets).
