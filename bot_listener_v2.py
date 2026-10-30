"""
Telegram Command Center v2 — Full Money Machine Bot
Upgraded bot_listener with lead hunting, DM blasting, earning tracking,
and auto-scheduling capabilities. Runs 24/7 on Samsung J7 Max via Termux.

Commands:
  /start, /help     — Show all commands
  /hunt              — Scan all platforms for leads NOW
  /hunt upwork       — Scan only Upwork
  /hunt ig <hashtag> — Search Instagram by hashtag
  /hunt li <role>    — Search LinkedIn by role
  /leads             — Show leads summary
  /leads hot         — Show 70+ score leads only
  /blast <N>         — Generate N personalized DMs for top leads
  /proposal <job>    — Generate Upwork proposal
  /dm <name> <biz>   — Generate outreach DM
  /earn              — Show earning dashboard
  /earn add <amt> <stream>  — Log new income
  /earn pipe <amt> <stream> <client> — Add pipeline deal
  /earn goal <amt>   — Set monthly goal
  /schedule <mins>   — Set auto-hunt interval
  /status            — Server health check
"""

import time
import requests
import json
import os
import sys
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Fix Windows Unicode encoding issues
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from proposal_generator import generate_upwork_proposal, generate_dm_outreach, answer_ai_question
import telegram_notifier
from lead_hunter import (
    hunt_all_platforms, get_hot_leads, get_leads_summary,
    generate_personalized_dm, auto_generate_dms, mark_lead_contacted,
    scrape_upwork_rss, search_google_leads, search_instagram_leads,
    search_linkedin_leads, load_leads_db, save_leads_db
)
from earning_tracker import (
    add_earning, add_pipeline_deal, update_pipeline_stage,
    format_earnings_telegram, format_pipeline_telegram, set_goal,
    get_monthly_summary
)

# --- Config ---
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# Auto-hunt state
auto_hunt_active = False
auto_hunt_interval = 30  # minutes
auto_hunt_thread = None


# --- HTTP Health Server (for cloud hosting compatibility) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        summary = get_monthly_summary()
        status = (
            f"Antigravity AI Money Machine - ACTIVE 24/7\n"
            f"Leads in DB: {get_leads_summary().get('total', 0)}\n"
            f"This Month: Rs.{summary.get('total_earned', 0):,.0f}\n"
            f"Pipeline: Rs.{summary.get('pipeline_value', 0):,.0f}\n"
            f"Auto-Hunt: {'ON' if auto_hunt_active else 'OFF'}"
        )
        self.wfile.write(status.encode("utf-8"))

    def log_message(self, fmt, *args):
        return  # Silence logs

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[INFO] Health server on port {port}")
    server.serve_forever()


# --- Telegram Polling ---
def get_updates(offset=None):
    config = load_config()
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
        print(f"[ERROR] Poll failed: {e}")
    return []


def send(text, chat_id):
    """Send message via Telegram (handles long messages by splitting)"""
    if len(text) > 4000:
        # Split long messages
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            telegram_notifier.send_message(chunk, chat_id=chat_id)
            time.sleep(0.5)
    else:
        telegram_notifier.send_message(text, chat_id=chat_id)


# --- Command Handlers ---

def cmd_help(chat_id):
    """Show all available commands"""
    msg = (
        "🚀 *ANTIGRAVITY MONEY MACHINE v2*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 *LEAD HUNTING:*\n"
        "• `/hunt` — Scan ALL platforms now\n"
        "• `/hunt upwork` — Upwork jobs only\n"
        "• `/hunt ig <hashtag>` — Instagram search\n"
        "• `/hunt li <role>` — LinkedIn search\n"
        "• `/hunt google <query>` — Google B2B search\n\n"
        "📋 *LEADS:*\n"
        "• `/leads` — Full summary\n"
        "• `/leads hot` — 70+ score leads\n"
        "• `/leads upwork` — Upwork leads only\n"
        "• `/leads ig` — Instagram leads only\n\n"
        "✉️ *OUTREACH:*\n"
        "• `/blast <N>` — Auto-DM top N leads\n"
        "• `/proposal <job>` — Upwork proposal\n"
        "• `/dm <name> <industry>` — Cold DM\n\n"
        "💰 *EARNINGS:*\n"
        "• `/earn` — Dashboard\n"
        "• `/earn add <₹> <stream>` — Log income\n"
        "• `/earn pipe <₹> <stream> <client>` — Pipeline deal\n"
        "• `/earn stage <client> <stage>` — Update deal stage\n"
        "• `/earn goal <₹>` — Set monthly goal\n"
        "• `/earn pipeline` — View pipeline\n\n"
        "⚙️ *SYSTEM:*\n"
        "• `/schedule <mins>` — Auto-hunt interval\n"
        "• `/schedule off` — Stop auto-hunt\n"
        "• `/status` — Server health\n\n"
        "💡 Or just type any question and AI will answer!"
    )
    send(msg, chat_id)


def cmd_hunt(args, chat_id):
    """Handle /hunt command with optional platform filter"""
    platform = args.strip().lower() if args else "all"

    if platform in ["all", ""]:
        send("🔍 *Scanning ALL platforms...* This takes 30-60 seconds.", chat_id)
        try:
            summary = hunt_all_platforms()
            msg = f"✅ *HUNT COMPLETE!*\n\n"
            msg += f"📊 *{summary['new_leads']}* new leads found\n"
            msg += f"📦 Total in database: {summary['total_leads']}\n\n"

            if summary["by_source"]:
                emojis = {"upwork": "💼", "google_search": "🔍", "instagram": "📸", "linkedin": "🔗"}
                msg += "*By Platform:*\n"
                for src, count in summary["by_source"].items():
                    msg += f"  {emojis.get(src, '•')} {src}: {count}\n"

            if summary["top_leads"]:
                msg += "\n*🔥 Top Leads:*\n"
                for i, lead in enumerate(summary["top_leads"][:5], 1):
                    msg += f"{i}. `[{lead['score']}%]` {lead['title'][:50]}\n"
                    if lead.get("url"):
                        msg += f"   🔗 {lead['url'][:60]}\n"

            msg += "\nUse `/leads hot` to see all hot leads\nUse `/blast 5` to generate DMs"
            send(msg, chat_id)
        except Exception as e:
            send(f"❌ Hunt error: {e}", chat_id)

    elif platform == "upwork":
        send("💼 *Scanning Upwork RSS feeds...*", chat_id)
        try:
            leads = scrape_upwork_rss()
            db = load_leads_db()
            existing = {l["id"] for l in db["leads"]}
            new = [l for l in leads if l["id"] not in existing]
            db["leads"].extend(new)
            db["leads"].sort(key=lambda x: x.get("score", 0), reverse=True)
            save_leads_db(db)

            msg = f"💼 *Upwork Scan: {len(new)} new jobs found!*\n\n"
            for i, lead in enumerate(sorted(new, key=lambda x: x.get("score", 0), reverse=True)[:5], 1):
                msg += f"{i}. `[{lead['score']}%]` *{lead['title'][:50]}*\n"
                msg += f"   💰 {lead.get('budget', 'N/A')}\n"
                if lead.get("url"):
                    msg += f"   🔗 {lead['url'][:60]}\n"
                msg += "\n"
            send(msg, chat_id)
        except Exception as e:
            send(f"❌ Upwork scan error: {e}", chat_id)

    elif platform.startswith("ig") or platform.startswith("insta"):
        hashtag = args.replace("ig", "").replace("instagram", "").strip().replace("#", "")
        hashtag = hashtag or "businessautomation"
        send(f"📸 *Searching Instagram for #{hashtag}...*", chat_id)
        try:
            leads = search_instagram_leads(hashtag)
            db = load_leads_db()
            existing = {l["id"] for l in db["leads"]}
            new = [l for l in leads if l["id"] not in existing]
            db["leads"].extend(new)
            save_leads_db(db)

            msg = f"📸 *Instagram: {len(new)} new profiles found!*\n\n"
            for i, lead in enumerate(new[:5], 1):
                msg += f"{i}. {lead['title']}\n"
                if lead.get("url"):
                    msg += f"   🔗 {lead['url']}\n"
            if not new:
                msg += "_No new profiles found. Instagram may be rate-limiting. Try again in a few minutes._"
            send(msg, chat_id)
        except Exception as e:
            send(f"❌ Instagram scan error: {e}", chat_id)

    elif platform.startswith("li") or platform.startswith("linked"):
        role = args.replace("li", "").replace("linkedin", "").strip()
        role = role or "startup founder"
        send(f"🔗 *Searching LinkedIn for '{role}'...*", chat_id)
        try:
            leads = search_linkedin_leads(role)
            db = load_leads_db()
            existing = {l["id"] for l in db["leads"]}
            new = [l for l in leads if l["id"] not in existing]
            db["leads"].extend(new)
            save_leads_db(db)

            msg = f"🔗 *LinkedIn: {len(new)} profiles found!*\n\n"
            for i, lead in enumerate(new[:5], 1):
                msg += f"{i}. {lead['title']}\n"
                if lead.get("url"):
                    msg += f"   🔗 {lead['url']}\n"
            if not new:
                msg += "_No new profiles found. Try a different role keyword._"
            send(msg, chat_id)
        except Exception as e:
            send(f"❌ LinkedIn scan error: {e}", chat_id)

    elif platform.startswith("google") or platform.startswith("g "):
        query = args.replace("google", "").replace("g ", "", 1).strip()
        query = query or "small business needs automation"
        send(f"🔍 *Searching Google for: '{query}'...*", chat_id)
        try:
            leads = search_google_leads(query)
            db = load_leads_db()
            existing = {l["id"] for l in db["leads"]}
            new = [l for l in leads if l["id"] not in existing]
            db["leads"].extend(new)
            save_leads_db(db)

            msg = f"🔍 *Google: {len(new)} businesses found!*\n\n"
            for i, lead in enumerate(new[:5], 1):
                msg += f"{i}. {lead['title'][:50]}\n"
                msg += f"   {lead['description'][:80]}...\n"
            send(msg, chat_id)
        except Exception as e:
            send(f"❌ Google search error: {e}", chat_id)

    else:
        send("❓ Unknown platform. Use: `/hunt`, `/hunt upwork`, `/hunt ig`, `/hunt li`, `/hunt google <query>`", chat_id)


def cmd_leads(args, chat_id):
    """Handle /leads command"""
    filter_type = args.strip().lower() if args else ""

    if filter_type == "hot":
        hot = get_hot_leads(min_score=70, limit=10)
        if not hot:
            send("🔥 No hot leads (70+ score) found yet. Run `/hunt` first!", chat_id)
            return

        msg = f"🔥 *HOT LEADS ({len(hot)} leads, score 70+):*\n\n"
        for i, lead in enumerate(hot, 1):
            msg += f"*{i}. [{lead['score']}%] {lead['title'][:45]}*\n"
            msg += f"   📍 Source: {lead['source']}\n"
            if lead.get("budget") and lead["budget"] != "Not specified":
                msg += f"   💰 {lead['budget']}\n"
            if lead.get("url"):
                msg += f"   🔗 {lead['url'][:55]}\n"
            msg += f"   📅 {lead.get('found_at', '')[:10]}\n\n"

        msg += "Use `/blast 5` to auto-generate DMs for these leads"
        send(msg, chat_id)

    elif filter_type in ["upwork", "instagram", "ig", "linkedin", "li", "google", "google_search"]:
        # Map shorthand to actual source names
        source_map = {"ig": "instagram", "li": "linkedin", "google": "google_search"}
        source = source_map.get(filter_type, filter_type)

        db = load_leads_db()
        filtered = [l for l in db["leads"] if l.get("source") == source]
        filtered.sort(key=lambda x: x.get("score", 0), reverse=True)

        if not filtered:
            send(f"📭 No {source} leads found yet. Run `/hunt {filter_type}` to scan!", chat_id)
            return

        emojis = {"upwork": "💼", "instagram": "📸", "linkedin": "🔗", "google_search": "🔍"}
        msg = f"{emojis.get(source, '📋')} *{source.upper()} LEADS ({len(filtered)} total):*\n\n"
        for i, lead in enumerate(filtered[:10], 1):
            status_icon = "✅" if lead.get("dm_sent") else "🆕"
            msg += f"{status_icon} {i}. `[{lead['score']}%]` {lead['title'][:45]}\n"
        send(msg, chat_id)

    else:
        # Full summary
        summary = get_leads_summary()

        if summary["total"] == 0:
            send("📭 *No leads yet!* Run `/hunt` to start scanning all platforms.", chat_id)
            return

        msg = f"📊 *LEADS DATABASE SUMMARY*\n\n"
        msg += f"📦 *Total Leads:* {summary['total']}\n"
        msg += f"🔥 *Hot Leads (70+):* {summary['hot_leads']}\n"
        msg += f"✉️ *DMs Sent:* {summary['total_dms_sent']}\n\n"

        if summary["by_source"]:
            emojis = {"upwork": "💼", "google_search": "🔍", "instagram": "📸", "linkedin": "🔗"}
            msg += "*By Platform:*\n"
            for src, count in summary["by_source"].items():
                msg += f"  {emojis.get(src, '•')} {src}: {count} leads\n"

        msg += f"\n*By Status:*\n"
        for status, count in summary["by_status"].items():
            if count > 0:
                icons = {"new": "🆕", "contacted": "✉️", "replied": "💬", "converted": "💰"}
                msg += f"  {icons.get(status, '•')} {status}: {count}\n"

        if summary.get("last_scan"):
            msg += f"\n🕐 Last scan: {summary['last_scan'][:16]}"

        msg += "\n\nCommands: `/leads hot` | `/leads upwork` | `/blast 5`"
        send(msg, chat_id)


def cmd_blast(args, chat_id):
    """Generate personalized DMs for top leads"""
    try:
        count = int(args.strip()) if args and args.strip().isdigit() else 5
    except ValueError:
        count = 5

    count = min(count, 10)  # Cap at 10

    send(f"✉️ *Generating {count} personalized DMs...* This may take a minute.", chat_id)

    try:
        results = auto_generate_dms(count)

        if not results:
            send("📭 No leads available for DM generation. Run `/hunt` first!", chat_id)
            return

        for i, result in enumerate(results, 1):
            lead = result["lead"]
            dm = result["dm"]
            style = result["style"]

            msg = f"━━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"✉️ *DM #{i} — {style.replace('_', ' ').title()}*\n"
            msg += f"*To:* {lead['title'][:50]}\n"
            msg += f"*Score:* {lead['score']}% | *Source:* {lead['source']}\n"
            if lead.get("url"):
                msg += f"*Link:* {lead['url'][:55]}\n"
            msg += f"\n```\n{dm}\n```\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━━"

            send(msg, chat_id)
            time.sleep(1)  # Avoid Telegram rate limits

        send(
            f"✅ *{len(results)} DMs generated!*\n\n"
            f"Copy-paste these to the respective platforms.\n"
            f"After sending, use `/earn add <amount> <stream>` when you close a deal! 💰",
            chat_id
        )

    except Exception as e:
        send(f"❌ DM generation error: {e}", chat_id)


def cmd_earn(args, chat_id):
    """Handle /earn commands"""
    parts = args.strip().split() if args else []
    sub = parts[0].lower() if parts else ""

    if sub == "add" and len(parts) >= 3:
        # /earn add 5000 upwork
        try:
            amount = float(parts[1].replace(",", "").replace("₹", ""))
            stream = parts[2].lower()
            desc = " ".join(parts[3:]) if len(parts) > 3 else ""

            valid_streams = ["upwork", "instagram", "linkedin", "realestate",
                           "bot_service", "lead_gen", "affiliate", "other"]
            if stream not in valid_streams:
                send(f"❌ Invalid stream. Use one of: {', '.join(valid_streams)}", chat_id)
                return

            entry = add_earning(amount, stream, description=desc)
            send(
                f"✅ *Income Logged!*\n\n"
                f"💰 Amount: ₹{amount:,.0f}\n"
                f"📂 Stream: {stream}\n"
                f"📅 Date: {datetime.now().strftime('%d %b %Y')}\n\n"
                f"Use `/earn` to see your updated dashboard!",
                chat_id
            )
        except (ValueError, IndexError):
            send("❌ Usage: `/earn add <amount> <stream>`\nExample: `/earn add 15000 upwork`", chat_id)

    elif sub == "pipe" and len(parts) >= 4:
        # /earn pipe 50000 bot_service ClientName
        try:
            amount = float(parts[1].replace(",", "").replace("₹", ""))
            stream = parts[2].lower()
            client = " ".join(parts[3:])

            deal = add_pipeline_deal(amount, stream, client)
            send(
                f"📋 *Pipeline Deal Added!*\n\n"
                f"💰 Value: ₹{amount:,.0f}\n"
                f"📂 Stream: {stream}\n"
                f"👤 Client: {client}\n"
                f"📍 Stage: prospect\n\n"
                f"Use `/earn stage {client} negotiation` to update",
                chat_id
            )
        except (ValueError, IndexError):
            send("❌ Usage: `/earn pipe <amount> <stream> <client name>`", chat_id)

    elif sub == "stage" and len(parts) >= 3:
        # /earn stage ClientName agreed
        stage = parts[-1].lower()
        client = " ".join(parts[1:-1])

        valid_stages = ["prospect", "negotiation", "agreed", "delivered", "paid"]
        if stage not in valid_stages:
            send(f"❌ Invalid stage. Use one of: {', '.join(valid_stages)}", chat_id)
            return

        result = update_pipeline_stage(client, stage)
        if result:
            msg = f"✅ *Deal Updated!*\n\n👤 {client} → *{stage.upper()}*"
            if stage == "paid":
                msg += f"\n\n💰 ₹{result['amount']:,.0f} moved to EARNED! 🎉"
            send(msg, chat_id)
        else:
            send(f"❌ Client '{client}' not found in pipeline.", chat_id)

    elif sub == "goal" and len(parts) >= 2:
        # /earn goal 100000
        try:
            amount = float(parts[1].replace(",", "").replace("₹", ""))
            set_goal(amount)
            send(f"🎯 *Monthly goal set to ₹{amount:,.0f}!*", chat_id)
        except ValueError:
            send("❌ Usage: `/earn goal <amount>`", chat_id)

    elif sub == "pipeline":
        send(format_pipeline_telegram(), chat_id)

    else:
        # Default: show dashboard
        send(format_earnings_telegram(), chat_id)


def cmd_schedule(args, chat_id):
    """Handle /schedule command for auto-hunt"""
    global auto_hunt_active, auto_hunt_interval, auto_hunt_thread

    arg = args.strip().lower() if args else ""

    if arg == "off" or arg == "stop":
        auto_hunt_active = False
        send("⏹️ *Auto-hunt STOPPED.* Manual hunting still available via `/hunt`.", chat_id)
        return

    if arg.isdigit():
        minutes = int(arg)
        if minutes < 5:
            send("⚠️ Minimum interval is 5 minutes (to avoid rate limits).", chat_id)
            return
        auto_hunt_interval = minutes
    else:
        auto_hunt_interval = 30

    if not auto_hunt_active:
        auto_hunt_active = True

        def hunt_loop():
            while auto_hunt_active:
                try:
                    summary = hunt_all_platforms()
                    if summary["new_leads"] > 0:
                        msg = f"🤖 *AUTO-HUNT REPORT*\n\n"
                        msg += f"Found *{summary['new_leads']}* new leads!\n\n"
                        if summary["top_leads"]:
                            for i, lead in enumerate(summary["top_leads"][:3], 1):
                                msg += f"{i}. `[{lead['score']}%]` {lead['title'][:40]}\n"
                        msg += f"\nNext scan in {auto_hunt_interval} min..."
                        send(msg, chat_id)

                        # Auto-generate DMs for very hot leads
                        hot = get_hot_leads(min_score=80, limit=2)
                        if hot:
                            dm_msg = "🔥 *HOT LEAD DMs READY:*\n\n"
                            for lead in hot:
                                dm = generate_personalized_dm(lead)
                                dm_msg += f"*To: {lead['title'][:40]}*\n"
                                dm_msg += f"```\n{dm[:300]}\n```\n\n"
                            send(dm_msg, chat_id)

                except Exception as e:
                    print(f"[AUTO-HUNT ERROR] {e}")

                # Sleep in 30-second chunks so we can stop faster
                for _ in range(auto_hunt_interval * 2):
                    if not auto_hunt_active:
                        break
                    time.sleep(30)

        auto_hunt_thread = threading.Thread(target=hunt_loop, daemon=True)
        auto_hunt_thread.start()

    send(
        f"🤖 *Auto-Hunt ACTIVATED!*\n\n"
        f"⏰ Scanning every *{auto_hunt_interval} minutes*\n"
        f"📡 Platforms: Upwork, Google, LinkedIn, Instagram\n"
        f"🔔 You'll get notified when hot leads are found\n\n"
        f"Use `/schedule off` to stop",
        chat_id
    )


def cmd_status(chat_id):
    """Show full system status"""
    summary = get_leads_summary()
    earn_summary = get_monthly_summary()

    msg = (
        "⚡ *MONEY MACHINE STATUS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📱 *Host:* Samsung Galaxy J7 Max (Termux)\n"
        f"🟢 *Bot:* Online & Listening\n"
        f"🤖 *Auto-Hunt:* {'🟢 Active (' + str(auto_hunt_interval) + 'min)' if auto_hunt_active else '🔴 Off'}\n\n"
        f"📊 *Leads:* {summary.get('total', 0)} total | {summary.get('hot_leads', 0)} hot\n"
        f"✉️ *DMs Sent:* {summary.get('total_dms_sent', 0)}\n\n"
        f"💰 *This Month:* ₹{earn_summary.get('total_earned', 0):,.0f} / ₹{earn_summary.get('goal', 100000):,.0f}\n"
        f"📋 *Pipeline:* ₹{earn_summary.get('pipeline_value', 0):,.0f}\n\n"
        f"🕐 *Last Scan:* {summary.get('last_scan', 'Never')[:16] if summary.get('last_scan') else 'Never'}\n"
        f"📅 *Uptime Since:* {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    send(msg, chat_id)


# --- Main Message Router ---
def handle_message(text: str, chat_id: int):
    """Route incoming messages to the right handler"""
    text_clean = text.strip()
    text_lower = text_clean.lower()

    # Greetings
    if text_lower in ["hi", "hello", "hey", "yo", "sup"] or text_clean.startswith("/start"):
        cmd_help(chat_id)
        return

    if text_clean.startswith("/help"):
        cmd_help(chat_id)
        return

    # Lead Hunting
    if text_clean.startswith("/hunt"):
        args = text_clean[5:].strip()
        cmd_hunt(args, chat_id)
        return

    # Leads View
    if text_clean.startswith("/leads"):
        args = text_clean[6:].strip()
        cmd_leads(args, chat_id)
        return

    # Blast DMs
    if text_clean.startswith("/blast"):
        args = text_clean[6:].strip()
        cmd_blast(args, chat_id)
        return

    # Proposals (legacy command preserved)
    if text_clean.startswith("/proposal") or text_lower.startswith("proposal:"):
        job = text_clean.replace("/proposal", "").replace("proposal:", "").strip()
        if not job:
            send("Usage: `/proposal <job description>`\nExample: `/proposal Build a Telegram bot with Python`", chat_id)
            return
        send("⏳ *Drafting your proposal...*", chat_id)
        draft = generate_upwork_proposal(job)
        send(draft, chat_id)
        return

    # DM Outreach (legacy command preserved)
    if text_clean.startswith("/dm"):
        parts = text_clean[3:].strip().split(" ", 1)
        name = parts[0] if parts and parts[0] else "Founder"
        biz = parts[1] if len(parts) > 1 else "Automation Agency"
        dm = generate_dm_outreach(name, biz)
        send(dm, chat_id)
        return

    # Earnings
    if text_clean.startswith("/earn"):
        args = text_clean[5:].strip()
        cmd_earn(args, chat_id)
        return

    # Schedule
    if text_clean.startswith("/schedule"):
        args = text_clean[9:].strip()
        cmd_schedule(args, chat_id)
        return

    # Status
    if text_clean.startswith("/status"):
        cmd_status(chat_id)
        return

    # Catch-all: AI answers any other question
    ai_answer = answer_ai_question(text_clean)
    send(ai_answer, chat_id)


# --- Main Daemon ---
def run_daemon():
    print("-" * 50)
    print("[*] ANTIGRAVITY MONEY MACHINE v2 -- STARTING")
    print(f"[*] {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("-" * 50)

    offset = None

    # Mark existing messages as read
    initial = get_updates()
    if initial:
        offset = initial[-1]["update_id"] + 1

    # Send startup notification
    config = load_config()
    owner_chat = config.get("chat_id")
    if owner_chat:
        send(
            "🟢 *Money Machine is ONLINE!*\n\n"
            "Your Samsung J7 Max is now running 24/7.\n"
            "Type `/help` to see all commands.\n"
            "Type `/hunt` to start finding leads immediately!",
            owner_chat
        )

    print("[INFO] Listening for Telegram messages...")

    while True:
        try:
            updates = get_updates(offset=offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if msg and "text" in msg:
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    sender = msg.get("from", {}).get("first_name", "Unknown")
                    print(f"[MSG] {sender}: {text}")
                    handle_message(text, chat_id)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    # Health server for cloud hosts
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Main bot loop
    run_daemon()
