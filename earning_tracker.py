"""
Earning Tracker — Multi-Stream Income Dashboard
Tracks income across all 7 earning streams from the J7 Max.
Stores data in JSON, generates reports via Telegram.
"""

import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EARNINGS_PATH = os.path.join(BASE_DIR, "earnings.json")


def load_earnings():
    """Load earnings database"""
    if os.path.exists(EARNINGS_PATH):
        try:
            with open(EARNINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "entries": [],
        "streams": {
            "upwork": {"name": "Upwork Freelancing", "emoji": "💼", "total": 0},
            "instagram": {"name": "Instagram Clients", "emoji": "📸", "total": 0},
            "linkedin": {"name": "LinkedIn Clients", "emoji": "🔗", "total": 0},
            "realestate": {"name": "Real Estate Commissions", "emoji": "🏠", "total": 0},
            "bot_service": {"name": "Bot-as-a-Service", "emoji": "🤖", "total": 0},
            "lead_gen": {"name": "Lead Gen Service", "emoji": "📊", "total": 0},
            "affiliate": {"name": "Affiliate/Referral", "emoji": "🔄", "total": 0},
            "other": {"name": "Other Income", "emoji": "💵", "total": 0}
        },
        "goal": 100000,  # ₹1,00,000 monthly goal
        "currency": "INR",
        "created_at": datetime.now().isoformat()
    }


def save_earnings(db):
    """Save earnings database"""
    with open(EARNINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False, default=str)


def add_earning(amount, stream, description="", client=""):
    """
    Add a new earning entry.
    stream: upwork, instagram, linkedin, realestate, bot_service, lead_gen, affiliate, other
    """
    db = load_earnings()

    entry = {
        "amount": float(amount),
        "stream": stream,
        "description": description,
        "client": client,
        "date": datetime.now().isoformat(),
        "month": datetime.now().strftime("%Y-%m")
    }

    db["entries"].append(entry)

    # Update stream total
    if stream in db["streams"]:
        db["streams"][stream]["total"] += float(amount)

    save_earnings(db)
    return entry


def add_pipeline_deal(amount, stream, client, stage="prospect", description=""):
    """
    Add a deal to the pipeline (not earned yet, but in progress).
    Stages: prospect → negotiation → agreed → delivered → paid
    """
    db = load_earnings()

    if "pipeline" not in db:
        db["pipeline"] = []

    deal = {
        "amount": float(amount),
        "stream": stream,
        "client": client,
        "stage": stage,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    db["pipeline"].append(deal)
    save_earnings(db)
    return deal


def update_pipeline_stage(client, new_stage):
    """Move a pipeline deal to a new stage"""
    db = load_earnings()

    for deal in db.get("pipeline", []):
        if deal["client"].lower() == client.lower():
            deal["stage"] = new_stage
            deal["updated_at"] = datetime.now().isoformat()

            # If paid, move to earnings
            if new_stage == "paid":
                add_earning(deal["amount"], deal["stream"],
                           description=deal.get("description", ""),
                           client=deal["client"])

            save_earnings(db)
            return deal

    return None


def get_monthly_summary(month=None):
    """Get earnings summary for a specific month (default: current month)"""
    db = load_earnings()

    if month is None:
        month = datetime.now().strftime("%Y-%m")

    month_entries = [e for e in db["entries"] if e.get("month") == month]

    total = sum(e["amount"] for e in month_entries)
    by_stream = {}

    for entry in month_entries:
        stream = entry["stream"]
        if stream not in by_stream:
            stream_info = db["streams"].get(stream, {"name": stream, "emoji": "💵"})
            by_stream[stream] = {
                "name": stream_info["name"],
                "emoji": stream_info["emoji"],
                "total": 0,
                "count": 0
            }
        by_stream[stream]["total"] += entry["amount"]
        by_stream[stream]["count"] += 1

    # Pipeline value
    pipeline_value = sum(d["amount"] for d in db.get("pipeline", []) if d.get("stage") != "paid")
    pipeline_count = len([d for d in db.get("pipeline", []) if d.get("stage") != "paid"])

    goal = db.get("goal", 100000)
    progress = (total / goal * 100) if goal > 0 else 0

    return {
        "month": month,
        "total_earned": total,
        "goal": goal,
        "progress": min(100, progress),
        "by_stream": by_stream,
        "entry_count": len(month_entries),
        "pipeline_value": pipeline_value,
        "pipeline_count": pipeline_count,
        "all_time_total": sum(e["amount"] for e in db["entries"])
    }


def get_pipeline_summary():
    """Get pipeline deals summary"""
    db = load_earnings()
    pipeline = db.get("pipeline", [])

    stages = {
        "prospect": {"deals": [], "emoji": "🔍"},
        "negotiation": {"deals": [], "emoji": "💬"},
        "agreed": {"deals": [], "emoji": "🤝"},
        "delivered": {"deals": [], "emoji": "📦"},
        "paid": {"deals": [], "emoji": "✅"}
    }

    for deal in pipeline:
        stage = deal.get("stage", "prospect")
        if stage in stages:
            stages[stage]["deals"].append(deal)

    return stages


def format_earnings_telegram():
    """Format earnings as a Telegram message"""
    summary = get_monthly_summary()
    month_name = datetime.strptime(summary["month"], "%Y-%m").strftime("%B %Y")

    # Progress bar
    filled = int(summary["progress"] / 5)
    bar = "█" * filled + "░" * (20 - filled)

    msg = f"💰 *EARNING DASHBOARD — {month_name}*\n\n"
    msg += f"*Total Earned:* ₹{summary['total_earned']:,.0f}\n"
    msg += f"*Monthly Goal:* ₹{summary['goal']:,.0f}\n"
    msg += f"*Progress:* [{bar}] {summary['progress']:.1f}%\n\n"

    if summary["by_stream"]:
        msg += "*By Stream:*\n"
        for stream_key, data in sorted(summary["by_stream"].items(),
                                        key=lambda x: x[1]["total"], reverse=True):
            msg += f"  {data['emoji']} {data['name']}: ₹{data['total']:,.0f} ({data['count']} deals)\n"
    else:
        msg += "_No earnings recorded yet. Use `/earn add <amount> <stream>` to log income._\n"

    if summary["pipeline_value"] > 0:
        msg += f"\n*📋 Pipeline:* {summary['pipeline_count']} deals worth ₹{summary['pipeline_value']:,.0f}\n"

    if summary["all_time_total"] > summary["total_earned"]:
        msg += f"\n*🏆 All-Time Total:* ₹{summary['all_time_total']:,.0f}"

    return msg


def format_pipeline_telegram():
    """Format pipeline as a Telegram message"""
    stages = get_pipeline_summary()

    msg = "📋 *DEAL PIPELINE*\n\n"
    total_value = 0

    stage_order = ["prospect", "negotiation", "agreed", "delivered", "paid"]
    for stage_name in stage_order:
        stage = stages[stage_name]
        if stage["deals"]:
            msg += f"*{stage['emoji']} {stage_name.upper()}:*\n"
            for deal in stage["deals"]:
                msg += f"  • {deal['client']}: ₹{deal['amount']:,.0f} ({deal['stream']})\n"
                if stage_name != "paid":
                    total_value += deal["amount"]
            msg += "\n"

    if total_value > 0:
        msg += f"*💎 Total Pipeline Value:* ₹{total_value:,.0f}"
    else:
        msg += "_No deals in pipeline yet. Use `/earn pipe <amount> <stream> <client>` to add one._"

    return msg


def set_goal(amount):
    """Set monthly earning goal"""
    db = load_earnings()
    db["goal"] = float(amount)
    save_earnings(db)
    return float(amount)


if __name__ == "__main__":
    print(format_earnings_telegram())
