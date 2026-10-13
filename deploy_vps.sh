#!/bin/bash
# ========================================================
# 24/7 UBUNTU / DEBIAN CLOUD SERVER DEPLOYMENT SCRIPT
# For: AWS, DigitalOcean, Hetzner, Linode, Oracle Cloud
# ========================================================

echo "=== Deploying AI Telegram Bot to Linux Cloud Server ==="

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl

APP_DIR="/opt/ai_bot"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR
cd $APP_DIR

# Clone / copy your files into $APP_DIR
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Create systemd service for 24/7 reliability & auto-restart
cat << EOF | sudo tee /etc/systemd/system/ai-telegram-bot.service
[Unit]
Description=24/7 AI Telegram Bot Freelance Engine
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python bot_listener.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ai-telegram-bot
sudo systemctl restart ai-telegram-bot

echo ""
echo "=== DEPLOYMENT COMPLETE! ==="
echo "Check status anytime with: sudo systemctl status ai-telegram-bot"
echo "View live logs with: sudo journalctl -u ai-telegram-bot -f"
