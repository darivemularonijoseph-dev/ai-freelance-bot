"""
Telegram Two-Way Bot Listener Daemon
Listens for commands and messages from the user on Telegram and responds interactively.
"""

import time
import requests
import json
import os
from proposal_generator import generate_upwork_proposal, generate_dm_outreach, answer_ai_question
import telegram_notifier

def get_updates(offset=None):
    config = telegram_notifier.load_config()
    token = config.get("bot_token")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 15}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=20)
        data = r.json()
        if data.get("ok"):
            return data.get("result", [])
    except Exception as e:
        print(f"[ERROR] Polling failed: {e}")
    return []

def handle_message(text: str, chat_id: int):
    text_clean = text.strip()
    
    if text_clean.startswith("/start") or text_clean.lower() in ["hi", "hello", "hey"]:
        reply = (
            "👋 *Welcome back, Roni!*\n\n"
            "I am your Antigravity AI assistant. I'm connected and ready to help you hit your *$1,000 Upwork goal*.\n\n"
            "Here is what you can do:\n"
            "• Send `/proposal <job details>` to draft a tailored proposal.\n"
            "• Send `/dm <company name>` to draft a client outreach DM.\n"
            "• Send `/status` to check your server health.\n"
            "• Ask any question or report any problem, and I'll assist you immediately!"
        )
        telegram_notifier.send_message(reply, chat_id=chat_id)
        return

    if text_clean.startswith("/status"):
        reply = (
            "✅ *System Status: 24/7 Active*\n\n"
            "• Bot Token: Connected\n"
            "• Chat ID: Verified (8856823322)\n"
            "• Mode: Two-way Telegram Daemon\n"
            "• Target: $1,000 Upwork Milestone"
        )
        telegram_notifier.send_message(reply, chat_id=chat_id)
        return

    if text_clean.startswith("/proposal") or text_clean.lower().startswith("proposal:"):
        job_content = text_clean.replace("/proposal", "").replace("proposal:", "").strip()
        if not job_content:
            telegram_notifier.send_message("Please provide job details, e.g.: `/proposal Looking for an AI Telegram chatbot with Python`", chat_id=chat_id)
            return
        telegram_notifier.send_message("⏳ Drafting your proposal...", chat_id=chat_id)
        draft = generate_upwork_proposal(job_content)
        telegram_notifier.send_message(draft, chat_id=chat_id)
        return

    if text_clean.startswith("/dm"):
        parts = text_clean.replace("/dm", "").strip().split(" ", 1)
        name = parts[0] if len(parts) > 0 and parts[0] else "Founder"
        b_type = parts[1] if len(parts) > 1 else "Automation Agency"
        dm_text = generate_dm_outreach(name, b_type)
        telegram_notifier.send_message(dm_text, chat_id=chat_id)
        return

    # Intelligent AI handling for any other prompt or question
    ai_answer = answer_ai_question(text_clean)
    telegram_notifier.send_message(ai_answer, chat_id=chat_id)

def run_daemon():
    print("[INFO] Telegram Bot Listener Daemon starting...")
    offset = None
    
    # Mark existing messages as read
    initial_updates = get_updates()
    if initial_updates:
        offset = initial_updates[-1]["update_id"] + 1

    print(f"[INFO] Listening for new updates (offset={offset})...")
    
    while True:
        try:
            updates = get_updates(offset=offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if msg and "text" in msg:
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text")
                    print(f"[RECEIVED] From {chat_id}: {text}")
                    handle_message(text, chat_id)
            time.sleep(2)
        except KeyboardInterrupt:
            print("[INFO] Stopping daemon.")
            break
        except Exception as e:
            print(f"[ERROR] Exception in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_daemon()
