#!/usr/bin/env bash
set -e

APP_DIR="/home/ubuntu/Stocks"

echo "Updating system..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx

if [ ! -d "$APP_DIR" ]; then
  echo "Repo not found at $APP_DIR. Clone your repo into $APP_DIR."
  exit 1
fi

cd "$APP_DIR"

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f "$APP_DIR/.env" ]; then
  echo "Missing .env file. Create it using deploy/env.example."
  exit 1
fi

echo "Installing systemd services..."
sudo cp deploy/systemd/sefp-backend.service /etc/systemd/system/
sudo cp deploy/systemd/sefp-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sefp-backend
sudo systemctl enable sefp-app
sudo systemctl start sefp-backend
sudo systemctl start sefp-app

echo "Configuring Nginx..."
sudo cp deploy/nginx/sefp.conf /etc/nginx/sites-available/sefp.conf
sudo ln -sf /etc/nginx/sites-available/sefp.conf /etc/nginx/sites-enabled/sefp.conf
sudo nginx -t
sudo systemctl restart nginx

echo "Done. App should be available on port 80."
