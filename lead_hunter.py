"""
Lead Hunter Engine — Multi-Platform Lead Finder & Auto-DM Generator
Designed to run on Samsung Galaxy J7 Max via Termux (low RAM, no browser needed)

Platforms supported:
  - Upwork RSS feeds (job postings matching your skills)
  - Google Custom Search (find businesses needing automation)
  - Web scraping for public business directories
  - Manual lead import via Telegram

All leads are scored, stored, and ready for personalized AI outreach.
"""

import json
import os
import re
import time
import hashlib
import requests
from datetime import datetime, timedelta

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LEADS_DB_PATH = os.path.join(BASE_DIR, "leads_database.json")
DM_LOG_PATH = os.path.join(BASE_DIR, "dm_log.json")

# Skills to search for (what you offer)
SKILL_KEYWORDS = [
    "telegram bot", "discord bot", "whatsapp bot", "chatbot",
    "python automation", "web scraping", "lead generation",
    "ai automation", "n8n", "make.com", "zapier",
    "api integration", "data extraction", "crm automation",
    "llm", "gpt", "claude", "ai agent", "workflow automation"
]

# Upwork RSS feed URLs (these are the public category feeds)
UPWORK_RSS_FEEDS = [
    "https://www.upwork.com/ab/feed/jobs/rss?q=telegram+bot&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=python+automation&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=web+scraping&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=ai+chatbot&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=whatsapp+bot&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=lead+generation+automation&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=n8n+automation&sort=recency",
    "https://www.upwork.com/ab/feed/jobs/rss?q=api+integration&sort=recency",
]

# Business directories to scrape for B2B leads
BUSINESS_SEARCH_QUERIES = [
    "small business needs automation India",
    "startup looking for chatbot developer",
    "company needs lead generation bot",
    "real estate agency needs CRM automation",
    "ecommerce store automation services needed",
]


def load_config():
    """Load config.json"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_leads_db():
    """Load existing leads database"""
    if os.path.exists(LEADS_DB_PATH):
        try:
            with open(LEADS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"leads": [], "last_scan": None, "total_found": 0, "total_dms_sent": 0}


def save_leads_db(db):
    """Save leads database"""
    with open(LEADS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False, default=str)


def load_dm_log():
    """Load DM send log"""
    if os.path.exists(DM_LOG_PATH):
        try:
            with open(DM_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_dm_log(log):
    """Save DM send log"""
    with open(DM_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False, default=str)


def generate_lead_id(title, source):
    """Generate unique ID for a lead to avoid duplicates"""
    raw = f"{title}:{source}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ============================================
# PLATFORM 1: UPWORK JOB SCRAPER (RSS)
# ============================================
def scrape_upwork_rss():
    """
    Scrape Upwork public RSS feeds for matching jobs.
    These are public feeds that don't require authentication.
    Returns list of lead dicts.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G615F) AppleWebKit/537.36"
    }

    for feed_url in UPWORK_RSS_FEEDS:
        try:
            resp = requests.get(feed_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue

            # Parse RSS XML manually (no lxml dependency needed for Termux)
            content = resp.text

            # Extract items from RSS
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)

            for item in items[:5]:  # Top 5 per feed to stay lightweight
                title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', item)

                link_match = re.search(r'<link>(.*?)</link>', item)
                desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item, re.DOTALL)
                if not desc_match:
                    desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)

                pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item)

                if title_match:
                    title = title_match.group(1).strip()
                    link = link_match.group(1).strip() if link_match else ""
                    description = desc_match.group(1).strip() if desc_match else ""
                    pub_date = pub_match.group(1).strip() if pub_match else ""

                    # Clean HTML from description
                    description = re.sub(r'<[^>]+>', '', description)
                    description = description[:500]  # Truncate

                    # Extract budget if mentioned
                    budget = "Not specified"
                    budget_match = re.search(r'Budget[:\s]*\$?([\d,]+(?:\.\d+)?)', description, re.IGNORECASE)
                    if budget_match:
                        budget = f"${budget_match.group(1)}"
                    hourly_match = re.search(r'\$([\d]+(?:\.\d+)?)\s*[-–]\s*\$([\d]+(?:\.\d+)?)\s*/?\s*hr', description, re.IGNORECASE)
                    if hourly_match:
                        budget = f"${hourly_match.group(1)}-${hourly_match.group(2)}/hr"

                    # Score the lead
                    score = score_upwork_lead(title, description, budget)

                    lead = {
                        "id": generate_lead_id(title, "upwork"),
                        "source": "upwork",
                        "type": "job_posting",
                        "title": title,
                        "description": description,
                        "url": link,
                        "budget": budget,
                        "posted": pub_date,
                        "score": score,
                        "status": "new",
                        "dm_sent": False,
                        "found_at": datetime.now().isoformat()
                    }
                    leads.append(lead)

            time.sleep(1)  # Be polite between requests

        except Exception as e:
            print(f"[WARN] RSS feed error: {e}")
            continue

    return leads


def score_upwork_lead(title, description, budget):
    """
    Score a lead 0-100 based on how well it matches your skills and profitability.
    Higher = better match = DM first.
    """
    score = 50  # Base score
    text = f"{title} {description}".lower()

    # Skill match bonuses
    skill_matches = 0
    for keyword in SKILL_KEYWORDS:
        if keyword in text:
            skill_matches += 1
            score += 8

    # Budget bonuses
    if budget != "Not specified":
        try:
            amount = float(re.search(r'[\d,]+', budget.replace(",", "")).group())
            if amount >= 500:
                score += 15
            elif amount >= 200:
                score += 10
            elif amount >= 50:
                score += 5
        except Exception:
            pass

    # Red flags (lower score)
    red_flags = ["unpaid", "free", "volunteer", "intern", "test project", "$5", "$10"]
    for flag in red_flags:
        if flag in text:
            score -= 20

    # High-value signals
    high_value = ["urgent", "asap", "immediately", "ongoing", "long-term", "retainer", "monthly"]
    for signal in high_value:
        if signal in text:
            score += 10

    # Cap score
    return max(0, min(100, score))


# ============================================
# PLATFORM 2: GOOGLE SEARCH FOR B2B LEADS
# ============================================
def search_google_leads(query=None):
    """
    Search Google for businesses that might need automation services.
    Uses a lightweight approach without needing a browser.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G615F) AppleWebKit/537.36"
    }

    search_queries = [query] if query else BUSINESS_SEARCH_QUERIES

    for q in search_queries[:3]:  # Limit to 3 searches per run
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}"
        try:
            resp = requests.get(search_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue

            # Extract results from DuckDuckGo HTML
            results = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                resp.text, re.DOTALL
            )

            for url, title, snippet in results[:5]:
                title = re.sub(r'<[^>]+>', '', title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()

                # Extract actual URL from DuckDuckGo redirect
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = requests.utils.unquote(url_match.group(1))

                # Try to extract contact info
                contact = extract_contact_from_snippet(snippet, url)

                lead = {
                    "id": generate_lead_id(title, "google"),
                    "source": "google_search",
                    "type": "business",
                    "title": title,
                    "description": snippet[:300],
                    "url": url,
                    "budget": "To be discussed",
                    "contact": contact,
                    "score": score_business_lead(title, snippet),
                    "status": "new",
                    "dm_sent": False,
                    "found_at": datetime.now().isoformat()
                }
                leads.append(lead)

            time.sleep(2)

        except Exception as e:
            print(f"[WARN] Google search error: {e}")
            continue

    return leads


def extract_contact_from_snippet(snippet, url):
    """Try to extract email or social media contact from snippet/URL"""
    contact = {}

    # Email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', snippet)
    if email_match:
        contact["email"] = email_match.group()

    # Phone
    phone_match = re.search(r'[\+]?[\d\s\-()]{10,15}', snippet)
    if phone_match:
        contact["phone"] = phone_match.group().strip()

    # Instagram from URL
    if "instagram.com" in url:
        ig_match = re.search(r'instagram\.com/([^/?]+)', url)
        if ig_match:
            contact["instagram"] = ig_match.group(1)

    # LinkedIn from URL
    if "linkedin.com" in url:
        li_match = re.search(r'linkedin\.com/in/([^/?]+)', url)
        if li_match:
            contact["linkedin"] = li_match.group(1)

    return contact


def score_business_lead(title, description):
    """Score a B2B lead based on potential fit"""
    score = 40
    text = f"{title} {description}".lower()

    # Business signals
    biz_signals = ["agency", "startup", "founder", "ceo", "cto", "business owner",
                   "e-commerce", "saas", "real estate", "consulting", "marketing"]
    for signal in biz_signals:
        if signal in text:
            score += 10

    # Need signals
    need_signals = ["looking for", "hiring", "need help", "seeking", "wants to automate",
                    "manual process", "time consuming", "repetitive"]
    for signal in need_signals:
        if signal in text:
            score += 12

    return max(0, min(100, score))


# ============================================
# PLATFORM 3: INSTAGRAM BUSINESS SCRAPER
# ============================================
def search_instagram_leads(hashtag="automation"):
    """
    Search Instagram for business accounts using public web endpoints.
    Lightweight — no login required, uses public hashtag/search pages.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G615F) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml"
    }

    hashtags_to_search = [
        "businessautomation", "chatbotdevelopment", "pythondeveloper",
        "telegrambot", "leadgeneration", "startupindia",
        "smallbusinessowner", "digitalmarketing", "aiautomation"
    ]

    if hashtag and hashtag not in hashtags_to_search:
        hashtags_to_search.insert(0, hashtag)

    for tag in hashtags_to_search[:3]:
        try:
            # Use Instagram's public web search (no login needed)
            url = f"https://www.instagram.com/explore/tags/{tag}/?__a=1&__d=dis"
            resp = requests.get(url, headers=headers, timeout=10)

            # Instagram might block/redirect but we try
            if resp.status_code == 200 and "application/json" in resp.headers.get("content-type", ""):
                data = resp.json()
                # Extract edge nodes if available
                edges = (data.get("graphql", {})
                        .get("hashtag", {})
                        .get("edge_hashtag_to_media", {})
                        .get("edges", []))

                for edge in edges[:3]:
                    node = edge.get("node", {})
                    owner = node.get("owner", {})
                    caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                    caption = caption_edges[0]["node"]["text"] if caption_edges else ""

                    lead = {
                        "id": generate_lead_id(owner.get("id", ""), "instagram"),
                        "source": "instagram",
                        "type": "business_profile",
                        "title": f"IG: @{owner.get('username', 'unknown')}",
                        "description": caption[:200],
                        "url": f"https://instagram.com/{owner.get('username', '')}",
                        "contact": {"instagram": owner.get("username", "")},
                        "score": 55,
                        "status": "new",
                        "dm_sent": False,
                        "found_at": datetime.now().isoformat()
                    }
                    leads.append(lead)

            time.sleep(2)

        except Exception as e:
            print(f"[WARN] Instagram search error for #{tag}: {e}")
            continue

    return leads


# ============================================
# PLATFORM 4: LINKEDIN PUBLIC PROFILE SEARCH
# ============================================
def search_linkedin_leads(role="startup founder"):
    """
    Search for LinkedIn profiles via DuckDuckGo site search.
    No LinkedIn login required — uses public search results.
    """
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G615F) AppleWebKit/537.36"
    }

    queries = [
        f'site:linkedin.com/in "{role}" "automation" India',
        f'site:linkedin.com/in "founder" "chatbot" OR "AI" India',
        f'site:linkedin.com/in "CTO" "needs automation" OR "looking for developer"',
    ]

    for q in queries[:2]:
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}"
            resp = requests.get(search_url, headers=headers, timeout=15)

            if resp.status_code != 200:
                continue

            # Extract LinkedIn profile links
            profile_links = re.findall(
                r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-]+)',
                resp.text
            )

            for username in list(set(profile_links))[:5]:
                lead = {
                    "id": generate_lead_id(username, "linkedin"),
                    "source": "linkedin",
                    "type": "professional",
                    "title": f"LinkedIn: {username.replace('-', ' ').title()}",
                    "description": f"Found via LinkedIn search for '{role}'",
                    "url": f"https://linkedin.com/in/{username}",
                    "contact": {"linkedin": username},
                    "score": 60,
                    "status": "new",
                    "dm_sent": False,
                    "found_at": datetime.now().isoformat()
                }
                leads.append(lead)

            time.sleep(2)

        except Exception as e:
            print(f"[WARN] LinkedIn search error: {e}")
            continue

    return leads


# ============================================
# AI DM GENERATOR (Gemini-powered)
# ============================================
def generate_personalized_dm(lead, style="cold_outreach"):
    """
    Use Gemini AI to generate a personalized DM for a specific lead.
    Style can be: cold_outreach, upwork_proposal, follow_up, instagram_dm
    """
    config = load_config()
    api_key = config.get("gemini_api_key", "")

    if not api_key:
        return generate_template_dm(lead, style)

    prompts = {
        "cold_outreach": (
            f"Write a cold outreach DM (under 80 words) for a freelancer named Roni who offers "
            f"AI automation, chatbots, web scraping, and workflow automation services. "
            f"The prospect is: {lead.get('title', 'a business owner')}. "
            f"Context: {lead.get('description', '')[:200]}. "
            f"Make it casual, value-first (mention saving 15+ hrs/week), and end with a soft CTA. "
            f"No emojis spam. Professional but friendly."
        ),
        "upwork_proposal": (
            f"Write a concise Upwork proposal (under 150 words) using the Reverse Pyramid framework: "
            f"1. First 2 lines address the exact problem. "
            f"2. 3-step concrete plan with tech stack. "
            f"3. Offer a 60-second demo. "
            f"4. Low-friction CTA. "
            f"Job: {lead.get('title', '')} — {lead.get('description', '')[:300]}. "
            f"Sign as Roni. Keep it sharp, no filler."
        ),
        "instagram_dm": (
            f"Write a short, casual Instagram DM (under 50 words) from Roni, a freelance AI developer. "
            f"The prospect is @{lead.get('contact', {}).get('instagram', 'someone')} "
            f"who appears to be in: {lead.get('description', 'business')[:100]}. "
            f"Make it feel personal, not salesy. Mention one specific way automation can help them."
        ),
        "follow_up": (
            f"Write a friendly follow-up DM (under 60 words) from Roni checking in on a previous message. "
            f"Prospect: {lead.get('title', 'a prospect')}. "
            f"Add new value (mention a case study or quick win). Don't be pushy."
        )
    }

    prompt = prompts.get(style, prompts["cold_outreach"])

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 500}
        }
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        data = resp.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[WARN] Gemini DM generation error: {e}")

    return generate_template_dm(lead, style)


def generate_template_dm(lead, style="cold_outreach"):
    """Fallback template-based DMs when Gemini is unavailable"""
    name = lead.get("title", "there").split(":")[-1].strip()

    templates = {
        "cold_outreach": (
            f"Hey {name},\n\n"
            f"Noticed your work — really solid stuff. Quick question: are your team members "
            f"still handling lead qualification and follow-ups manually?\n\n"
            f"We recently built an AI workflow that cut response time to under 30 seconds "
            f"and freed up 15+ hours/week for a similar business.\n\n"
            f"Happy to share a 2-min breakdown if relevant. No pitch.\n\n"
            f"— Roni"
        ),
        "upwork_proposal": (
            f"Hi,\n\n"
            f"I reviewed your project and spotted the exact bottleneck — {lead.get('description', 'this')[:80]}.\n\n"
            f"Here's my 3-step plan:\n"
            f"1. Architecture: Lightweight Python + API solution with error handling\n"
            f"2. Reliability: Automated fail-safes for 24/7 operation\n"
            f"3. Turnaround: Working prototype in 48 hours\n\n"
            f"Want me to record a 60-second demo of the approach?\n\n"
            f"— Roni"
        ),
        "instagram_dm": (
            f"Hey! 👋 Love what you're building. I help businesses like yours save 15+ hrs/week "
            f"with AI automation. Would a quick 2-min case study be useful? No pressure at all. — Roni"
        ),
        "follow_up": (
            f"Hey {name}, just circling back — we shipped a similar automation last week that "
            f"saved a client 20 hrs/week on lead follow-ups. Thought it might be relevant for you. "
            f"Happy to share the framework if you're interested! — Roni"
        )
    }

    return templates.get(style, templates["cold_outreach"])


# ============================================
# MASTER HUNT FUNCTION
# ============================================
def hunt_all_platforms(custom_query=None):
    """
    Run lead hunting across all platforms.
    Returns summary dict with new leads found.
    """
    db = load_leads_db()
    existing_ids = {lead["id"] for lead in db["leads"]}
    new_leads = []

    print("[HUNT] 🔍 Scanning Upwork RSS feeds...")
    upwork_leads = scrape_upwork_rss()
    for lead in upwork_leads:
        if lead["id"] not in existing_ids:
            new_leads.append(lead)
            existing_ids.add(lead["id"])

    print("[HUNT] 🔍 Searching Google/DuckDuckGo for businesses...")
    google_leads = search_google_leads(custom_query)
    for lead in google_leads:
        if lead["id"] not in existing_ids:
            new_leads.append(lead)
            existing_ids.add(lead["id"])

    print("[HUNT] 🔍 Searching LinkedIn profiles...")
    linkedin_leads = search_linkedin_leads()
    for lead in linkedin_leads:
        if lead["id"] not in existing_ids:
            new_leads.append(lead)
            existing_ids.add(lead["id"])

    print("[HUNT] 🔍 Searching Instagram businesses...")
    ig_leads = search_instagram_leads()
    for lead in ig_leads:
        if lead["id"] not in existing_ids:
            new_leads.append(lead)
            existing_ids.add(lead["id"])

    # Add new leads to DB
    db["leads"].extend(new_leads)
    db["last_scan"] = datetime.now().isoformat()
    db["total_found"] += len(new_leads)

    # Sort by score (highest first)
    db["leads"].sort(key=lambda x: x.get("score", 0), reverse=True)

    save_leads_db(db)

    summary = {
        "new_leads": len(new_leads),
        "total_leads": len(db["leads"]),
        "by_source": {},
        "top_leads": []
    }

    for lead in new_leads:
        src = lead["source"]
        summary["by_source"][src] = summary["by_source"].get(src, 0) + 1

    # Top 5 highest scoring new leads
    summary["top_leads"] = sorted(new_leads, key=lambda x: x.get("score", 0), reverse=True)[:5]

    return summary


def get_hot_leads(min_score=70, limit=10):
    """Get top-scoring leads that haven't been contacted yet"""
    db = load_leads_db()
    hot = [l for l in db["leads"] if l.get("score", 0) >= min_score and not l.get("dm_sent")]
    return sorted(hot, key=lambda x: x.get("score", 0), reverse=True)[:limit]


def get_leads_summary():
    """Get a summary of all leads in the database"""
    db = load_leads_db()
    leads = db["leads"]

    total = len(leads)
    by_source = {}
    by_status = {"new": 0, "contacted": 0, "replied": 0, "converted": 0}
    hot_count = 0

    for lead in leads:
        src = lead.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

        status = lead.get("status", "new")
        by_status[status] = by_status.get(status, 0) + 1

        if lead.get("score", 0) >= 70:
            hot_count += 1

    return {
        "total": total,
        "hot_leads": hot_count,
        "by_source": by_source,
        "by_status": by_status,
        "last_scan": db.get("last_scan"),
        "total_dms_sent": db.get("total_dms_sent", 0)
    }


def mark_lead_contacted(lead_id):
    """Mark a lead as contacted"""
    db = load_leads_db()
    for lead in db["leads"]:
        if lead["id"] == lead_id:
            lead["status"] = "contacted"
            lead["dm_sent"] = True
            lead["contacted_at"] = datetime.now().isoformat()
            break
    db["total_dms_sent"] = db.get("total_dms_sent", 0) + 1
    save_leads_db(db)


def auto_generate_dms(count=5):
    """Auto-generate personalized DMs for top leads"""
    hot_leads = get_hot_leads(min_score=50, limit=count)
    results = []

    for lead in hot_leads:
        # Choose DM style based on source
        style_map = {
            "upwork": "upwork_proposal",
            "instagram": "instagram_dm",
            "linkedin": "cold_outreach",
            "google_search": "cold_outreach"
        }
        style = style_map.get(lead["source"], "cold_outreach")

        dm_text = generate_personalized_dm(lead, style)
        results.append({
            "lead": lead,
            "dm": dm_text,
            "style": style
        })

    return results


# ============================================
# AUTO-HUNT SCHEDULER (runs every N minutes)
# ============================================
def auto_hunt_loop(interval_minutes=30, notify_telegram=True):
    """
    Continuous lead hunting loop.
    Runs every interval_minutes and sends results to Telegram.
    Designed to run 24/7 on the J7 Max via Termux.
    """
    import telegram_notifier

    print(f"[AUTO-HUNT] 🚀 Starting auto-hunt loop (every {interval_minutes} min)")
    telegram_notifier.send_message(
        f"🚀 *Lead Hunter ACTIVATED*\n\n"
        f"Scanning every {interval_minutes} minutes across:\n"
        f"• Upwork RSS feeds\n"
        f"• Google/DuckDuckGo B2B search\n"
        f"• LinkedIn public profiles\n"
        f"• Instagram business accounts\n\n"
        f"I'll notify you when I find hot leads! 🔥"
    )

    while True:
        try:
            summary = hunt_all_platforms()

            if summary["new_leads"] > 0 and notify_telegram:
                # Build Telegram notification
                msg = f"🎯 *NEW LEADS FOUND!*\n\n"
                msg += f"📊 *{summary['new_leads']}* new leads found\n"
                msg += f"📦 Total in database: {summary['total_leads']}\n\n"

                if summary["by_source"]:
                    msg += "*By Platform:*\n"
                    source_emojis = {
                        "upwork": "💼", "google_search": "🔍",
                        "instagram": "📸", "linkedin": "💼"
                    }
                    for src, count in summary["by_source"].items():
                        emoji = source_emojis.get(src, "•")
                        msg += f"  {emoji} {src}: {count}\n"

                if summary["top_leads"]:
                    msg += "\n*🔥 Hottest Leads:*\n"
                    for i, lead in enumerate(summary["top_leads"][:3], 1):
                        msg += f"{i}. [{lead['score']}%] {lead['title'][:50]}\n"

                msg += f"\nUse `/leads` to see all or `/blast` to auto-DM top leads"
                telegram_notifier.send_message(msg)

                # Auto-generate DMs for hot leads
                hot = get_hot_leads(min_score=75, limit=3)
                if hot:
                    dm_msg = "✉️ *AUTO-GENERATED DMs READY:*\n\n"
                    for lead in hot:
                        dm = generate_personalized_dm(lead)
                        dm_msg += f"*To: {lead['title'][:40]}*\n"
                        dm_msg += f"```\n{dm[:200]}\n```\n\n"
                    telegram_notifier.send_message(dm_msg)

            print(f"[AUTO-HUNT] ✅ Scan complete. {summary['new_leads']} new leads. Sleeping {interval_minutes}min...")

        except Exception as e:
            print(f"[AUTO-HUNT] ❌ Error: {e}")

        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        auto_hunt_loop(interval_minutes=interval)
    else:
        print("[HUNT] Running single scan across all platforms...")
        result = hunt_all_platforms()
        print(f"\n✅ Found {result['new_leads']} new leads!")
        print(f"📦 Total: {result['total_leads']}")
        for src, count in result.get("by_source", {}).items():
            print(f"  • {src}: {count}")

        hot = get_hot_leads()
        if hot:
            print(f"\n🔥 Top {len(hot)} Hot Leads:")
            for i, lead in enumerate(hot, 1):
                print(f"  {i}. [{lead['score']}%] {lead['title'][:60]} ({lead['source']})")
