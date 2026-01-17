# Oracle Free VM Deployment (Always Free)

This guide deploys the Streamlit app + FastAPI backend on an Oracle Cloud Always Free VM.

## 1) Create the VM (Oracle Cloud Always Free)
1. Sign up for Oracle Cloud Free Tier.
2. Create a **VM Instance**:
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (Always Free)
   - OCPUs: 1–2, RAM: 6–12 GB (within Always Free limits)
3. Add your **SSH public key**.
4. Open ports in **VCN Security List**:
   - TCP **80**
   - TCP **443** (optional, for HTTPS)
   - TCP **22** (SSH)

## 2) SSH into the VM
```bash
ssh ubuntu@<YOUR_PUBLIC_IP>
```

## 3) Install dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx
```

## 4) Clone the repo
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd Stocks
```

## 5) Create virtual environment & install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 6) Set environment variables
Create `.env` (use `deploy/.env.example` as a template):
```bash
cp deploy/.env.example .env
nano .env
```

Required values:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` → `https://<YOUR_DOMAIN_OR_IP>`
- `OPENAI_API_KEY`
- `SEFP_CHAT_BACKEND_URL` → `https://<YOUR_DOMAIN_OR_IP>/api/chat`

## 7) Install systemd services
Copy service files:
```bash
sudo cp deploy/systemd/sefp-backend.service /etc/systemd/system/
sudo cp deploy/systemd/sefp-app.service /etc/systemd/system/
```

Reload and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sefp-backend
sudo systemctl enable sefp-app
sudo systemctl start sefp-backend
sudo systemctl start sefp-app
```

Check status:
```bash
sudo systemctl status sefp-backend
sudo systemctl status sefp-app
```

## 8) Configure Nginx (reverse proxy)
```bash
sudo cp deploy/nginx/sefp.conf /etc/nginx/sites-available/sefp.conf
sudo ln -s /etc/nginx/sites-available/sefp.conf /etc/nginx/sites-enabled/sefp.conf
sudo nginx -t
sudo systemctl restart nginx
```

## 9) Open the app
Visit:
```
http://<YOUR_PUBLIC_IP>/
```

Google OAuth redirect URI must match your domain/IP:
```
http://<YOUR_PUBLIC_IP>
```

## Optional: HTTPS (recommended)
Use Let's Encrypt:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d <YOUR_DOMAIN>
```

Update `GOOGLE_REDIRECT_URI` to:
```
https://<YOUR_DOMAIN>
```

## Logs & Troubleshooting
```bash
journalctl -u sefp-backend -f
journalctl -u sefp-app -f
```

If chat fails:
- Check `OPENAI_API_KEY`
- Check `/api/chat` is reachable
  ```bash
  curl -X POST http://localhost:8000/chat
  ```
