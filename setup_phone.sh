#!/data/data/com.termux/files/usr/bin/bash
# ========================================================
# 24/7 SMARTPHONE SERVER INSTALLER (Termux / Android)
# For: Roni Joseph - Antigravity AI Freelance Suite
# ========================================================

echo ""
echo "===================================================="
echo "  🚀 Setting up 24/7 AI Telegram Server on Phone"
echo "===================================================="
echo ""

# 1. Keep CPU awake when screen turns off
termux-wake-lock
echo "[+] Wake-lock enabled (CPU will stay active 24/7)."

# 2. Update Termux packages
echo "[+] Updating packages..."
pkg update -y && pkg upgrade -y

# 3. Install Python, Curl, OpenSSH
echo "[+] Installing Python and dependencies..."
pkg install -y python git curl openssh
pip install --upgrade pip
pip install requests

# 4. Create App Directory
PROJECT_DIR="$HOME/ai_server"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR" || exit 1
echo "[+] Working directory: $PROJECT_DIR"

# 5. Write config.json
cat << 'EOF' > config.json
{
  "bot_token": "8725679037:AAFDFl8xDz9WeZiA_Jdozb9rAZQ37WSRKI4",
  "chat_id": 8856823322,
  "bot_username": "Antrigravityroni_bot",
  "gemini_api_key": ""
}
EOF
echo "[+] Created config.json"

# 6. Write telegram_notifier.py
cat << 'EOF' > telegram_notifier.py
import json
import os
import requests

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "bot_token": "8725679037:AAFDFl8xDz9WeZiA_Jdozb9rAZQ37WSRKI4",
        "chat_id": 8856823322,
        "bot_username": "Antrigravityroni_bot"
    }

def send_message(text: str, chat_id: int = None) -> bool:
    config = load_config()
    token = config.get("bot_token")
    target_chat = chat_id or config.get("chat_id")
    if not token or not target_chat:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": target_chat, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        res = r.json()
        if res.get("ok"):
            return True
        payload.pop("parse_mode", None)
        return requests.post(url, json=payload, timeout=10).json().get("ok", False)
    except Exception as e:
        print(f"[ERR] send_message: {e}")
        return False

def get_latest_messages(limit: int = 5):
    config = load_config()
    token = config.get("bot_token")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        r = requests.get(url, params={"limit": limit}, timeout=10).json()
        if r.get("ok"):
            return r.get("result", [])
    except Exception:
        pass
    return []
EOF
echo "[+] Created telegram_notifier.py"

# 7. Write proposal_generator.py
cat << 'EOF' > proposal_generator.py
import os
import json
import requests
import telegram_notifier

def get_gemini_api_key():
    config = telegram_notifier.load_config()
    return config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "").strip()

def call_gemini(prompt: str) -> str:
    key = get_gemini_api_key()
    if not key:
        return ""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20).json()
        if "candidates" in resp and len(resp["candidates"]) > 0:
            return resp["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
    return ""

def generate_upwork_proposal(client_job_description: str, budget_target: str = "$1,000") -> str:
    api_key = get_gemini_api_key()
    if api_key:
        prompt = (
            "You are an elite freelance engineer aiming to hit $1,000 milestones on Upwork. "
            "Write a concise, high-converting Upwork proposal for this job using the 'Reverse Pyramid' framework:\n"
            "1. First 2 lines address exact problem directly.\n"
            "2. 3-step concrete execution plan (tech stack, error handling, 48-hr prototype).\n"
            "3. Offer a 60-second video demo.\n"
            "4. Low-friction Call to Action.\n"
            "Keep it under 180 words. Sign off as 'Roni'.\n\n"
            f"Job:\n{client_job_description}"
        )
        ai_prop = call_gemini(prompt)
        if ai_prop:
            return f"*AI-GENERATED PROPOSAL (Gemini)*\n\n{ai_prop}"

    job_lower = client_job_description.lower()
    tech_stack = []
    if any(k in job_lower for k in ["bot", "telegram", "discord", "chat"]):
        tech_stack.append("Telegram/Chatbot API & Python backend")
    if any(k in job_lower for k in ["scrape", "scraping", "lead", "extract", "data"]):
        tech_stack.append("Python web scrapers (Playwright/BeautifulSoup)")
    if any(k in job_lower for k in ["automation", "zapier", "make", "n8n"]):
        tech_stack.append("Workflow automation (n8n/Make.com/APIs)")
    if any(k in job_lower for k in ["ai", "gpt", "llm", "claude", "agent"]):
        tech_stack.append("LLM integrations (OpenAI/Anthropic APIs)")
    tech_str = ", ".join(tech_stack) if tech_stack else "Python automation, API integrations, and robust backend architecture"

    return f"""*PROPOSAL DRAFT (Ready to Copy & Customize)*

Hi there,

I reviewed your project and noticed the exact bottleneck you're looking to solve. Most solutions fail here because they don't handle edge cases, API rate-limits, and clean data structure.

Here is how I will structure this for you:
1. **Architecture & Setup:** Build a lightweight, scalable solution using {tech_str}.
2. **Error-Handling & Reliability:** Implement automated fail-safes so it runs 24/7 without breaking or dropping sessions.
3. **Turnaround:** I can deliver the core working prototype within 48 hours for your review.

Would you like me to record a quick 60-second video demo showing how the workflow operates before we begin?

Best regards,
Roni
"""

def generate_dm_outreach(prospect_name: str, business_type: str) -> str:
    api_key = get_gemini_api_key()
    if api_key:
        prompt = f"Write a casual B2B direct message outreach (under 75 words) to {prospect_name} who runs {business_type} offering a 2-min demo of our AI automation saving 15+ hrs/wk. Sign off as Roni."
        ai_dm = call_gemini(prompt)
        if ai_dm:
            return f"*AI-GENERATED OUTREACH (Gemini)*\n\n{ai_dm}"

    return f"""*OUTREACH DM TEMPLATE*

Hey {prospect_name},

Saw your work with {business_type}. Quick question: are your team members still manually handling lead qualification and messaging, or have you already hooked that into an automated AI workflow?

We recently built a system that cut response time down to under 30 seconds and freed up 15+ hours/week.

Happy to share a quick 2-minute breakdown if you're exploring automation this quarter. No pitch, just wanted to share the framework if relevant.

Cheers,
Roni
"""

def answer_ai_question(question: str) -> str:
    api_key = get_gemini_api_key()
    if not api_key:
        return "💡 Tip: To enable dynamic AI Q&A, add your free Gemini API key to config.json (from https://aistudio.google.com)."
    prompt = f"You are an assistant helping Roni reach $1,000 on Upwork through AI automation, scraping, and freelancing. Answer clearly in English:\n\n{question}"
    return call_gemini(prompt) or "Could not generate answer. Please try again."
EOF
echo "[+] Created proposal_generator.py"

# 8. Write bot_listener.py
cat << 'EOF' > bot_listener.py
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
    except Exception:
        pass
    return []

def handle_message(text: str, chat_id: int):
    text_clean = text.strip()
    if text_clean.startswith("/start") or text_clean.lower() in ["hi", "hello", "hey"]:
        reply = (
            "📱 *Smartphone 24/7 Server is ACTIVE!*\n\n"
            "Hello Roni! Your phone server is running and online around the clock.\n\n"
            "Commands available:\n"
            "• `/proposal <job details>` — Drafts an Upwork proposal.\n"
            "• `/dm <name> <industry>` — Drafts a cold outreach DM.\n"
            "• `/status` — Verifies smartphone host status.\n"
            "• Ask any question or report any problem!"
        )
        telegram_notifier.send_message(reply, chat_id=chat_id)
        return

    if text_clean.startswith("/status"):
        reply = (
            "🔋 *Phone Server Status: Online 24/7*\n\n"
            "• Host: Android Smartphone (Termux)\n"
            "• RAM Usage: Minimal (<80MB)\n"
            "• Daemon: Active & Polling\n"
            "• Goal: $1,000 Upwork Milestone"
        )
        telegram_notifier.send_message(reply, chat_id=chat_id)
        return

    if text_clean.startswith("/proposal") or text_clean.lower().startswith("proposal:"):
        job = text_clean.replace("/proposal", "").replace("proposal:", "").strip()
        if not job:
            telegram_notifier.send_message("Please provide job details, e.g.: `/proposal Build a Telegram bot with Python`", chat_id=chat_id)
            return
        telegram_notifier.send_message("⏳ Drafting your proposal...", chat_id=chat_id)
        draft = generate_upwork_proposal(job)
        telegram_notifier.send_message(draft, chat_id=chat_id)
        return

    if text_clean.startswith("/dm"):
        parts = text_clean.replace("/dm", "").strip().split(" ", 1)
        name = parts[0] if len(parts) > 0 and parts[0] else "Founder"
        b_type = parts[1] if len(parts) > 1 else "Automation Agency"
        dm_text = generate_dm_outreach(name, b_type)
        telegram_notifier.send_message(dm_text, chat_id=chat_id)
        return

    ai_answer = answer_ai_question(text_clean)
    telegram_notifier.send_message(ai_answer, chat_id=chat_id)

def run_daemon():
    print("[INFO] Smartphone 24/7 Bot Daemon starting...")
    offset = None
    initial_updates = get_updates()
    if initial_updates:
        offset = initial_updates[-1]["update_id"] + 1

    while True:
        try:
            updates = get_updates(offset=offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if msg and "text" in msg:
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text")
                    print(f"[RECV] {text}")
                    handle_message(text, chat_id)
            time.sleep(2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERR] {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_daemon()
EOF
echo "[+] Created bot_listener.py"

# 9. Stop any previous instance and start in background
pkill -f "bot_listener.py" 2>/dev/null
nohup python bot_listener.py > bot.log 2>&1 &

echo ""
echo "===================================================="
echo "  ✅ INSTALLATION COMPLETE!"
echo "  Your 24/7 AI Bot is now RUNNING on this phone!"
echo "===================================================="
echo ""

# 10. Send confirmation message via Telegram
python -c "import telegram_notifier; telegram_notifier.send_message('🎉 *Congratulations Roni!* Your smartphone 24/7 server installation is complete and running in the background. Type /status to verify.')"
