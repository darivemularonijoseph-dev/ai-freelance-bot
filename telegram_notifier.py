"""
Telegram Notifier & Two-Way Communication Module
Supports reading credentials from environment variables (Cloud Server)
or config.json (Local file).
"""

import json
import os
import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    cfg = {
        "bot_token": os.environ.get("BOT_TOKEN", "").strip(),
        "chat_id": os.environ.get("CHAT_ID", "").strip(),
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", "").strip()
    }
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
                if not cfg["bot_token"]:
                    cfg["bot_token"] = file_cfg.get("bot_token", "")
                if not cfg["chat_id"]:
                    cfg["chat_id"] = file_cfg.get("chat_id", "")
                if not cfg["gemini_api_key"]:
                    cfg["gemini_api_key"] = file_cfg.get("gemini_api_key", "")
        except Exception as e:
            print(f"[WARN] Failed to read config.json: {e}")
            
    # Hardcoded fallbacks if nothing is provided
    if not cfg["bot_token"]:
        cfg["bot_token"] = "8725679037:AAFDFl8xDz9WeZiA_Jdozb9rAZQ37WSRKI4"
    if not cfg["chat_id"]:
        cfg["chat_id"] = 8856823322
        
    return cfg

def send_message(text: str, chat_id: int = None) -> bool:
    """Send a message to the user via Telegram."""
    config = load_config()
    token = config.get("bot_token")
    target_chat = chat_id or config.get("chat_id")
    
    if not token or not target_chat:
        print("[ERROR] Missing bot_token or chat_id.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_json = response.json()
        if res_json.get("ok"):
            return True
        else:
            payload.pop("parse_mode", None)
            fallback = requests.post(url, json=payload, timeout=10)
            return fallback.json().get("ok", False)
    except Exception as e:
        print(f"[EXCEPTION] Failed to send message: {e}")
        return False

def get_latest_messages(limit: int = 5):
    """Retrieve the latest messages sent by the user to the bot."""
    config = load_config()
    token = config.get("bot_token")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url, params={"limit": limit}, timeout=10)
        res = response.json()
        if res.get("ok"):
            return res.get("result", [])
    except Exception as e:
        print(f"[ERROR] Could not fetch updates: {e}")
    return []

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        send_message(msg)
    else:
        print("Telegram notifier ready.")
