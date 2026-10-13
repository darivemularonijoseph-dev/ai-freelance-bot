"""
High-Converting Proposal & DM Generator
Uses Google Gemini API if configured; otherwise falls back to smart structured frameworks.
"""

import os
import json
import requests
import telegram_notifier

def get_gemini_api_key():
    config = telegram_notifier.load_config()
    return config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "").strip()

def call_gemini(prompt: str) -> str:
    """Query Gemini 1.5/2.0 Flash via REST API."""
    key = get_gemini_api_key()
    if not key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        data = resp.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"[WARN] Gemini response error: {data}")
    except Exception as e:
        print(f"[ERROR] Failed to query Gemini API: {e}")
    return ""

def generate_upwork_proposal(client_job_description: str, budget_target: str = "$1,000") -> str:
    """
    Constructs a structured, human-like, non-generic proposal based on
    the client's specific requirements.
    """
    api_key = get_gemini_api_key()
    if api_key:
        prompt = (
            "You are an elite freelance engineer aiming to hit $1,000 milestones on Upwork. "
            "Write a concise, high-converting Upwork proposal for this job using the 'Reverse Pyramid' framework:\n"
            "1. First 2 lines must address their exact problem/bottleneck directly without saying 'Dear client' or 'I am an expert'.\n"
            "2. 3-step concrete execution plan (tech stack, error handling, 48-hour prototype turnaround).\n"
            "3. Offer a 60-second Loom/video demo.\n"
            "4. Low-friction Call to Action.\n"
            "Keep it under 180 words. Sign off as 'Roni'.\n\n"
            f"Client Job Posting:\n{client_job_description}"
        )
        ai_proposal = call_gemini(prompt)
        if ai_proposal:
            return f"*AI-GENERATED PROPOSAL (Gemini)*\n\n{ai_proposal}"

    # Fallback template mode
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
    """Generate cold direct message / outreach template for agencies/businesses."""
    api_key = get_gemini_api_key()
    if api_key:
        prompt = (
            f"Write a short, casual B2B direct message outreach (under 75 words) to {prospect_name} who runs {business_type}. "
            "Ask if they are still doing manual lead qualification/data entry, and offer to share a 2-minute video showing our AI automation that saves 15+ hrs/wk. "
            "No sales pitch, sign off as Roni."
        )
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
    """Answers arbitrary user freelancing/coding questions via Gemini."""
    api_key = get_gemini_api_key()
    if not api_key:
        return (
            "💡 *Tip:* To unlock full AI answers 24/7 on your bot, you can get a free Google Gemini API key from "
            "https://aistudio.google.com and add it to `config.json`."
        )
    prompt = (
        "You are an assistant helping Roni reach $1,000 on Upwork through AI automation, scraping, and freelancing. "
        f"Answer clearly and concisely in English:\n\n{question}"
    )
    res = call_gemini(prompt)
    return res or "Sorry, I had trouble generating a response. Please try again."
