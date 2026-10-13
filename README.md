# AI-Based DMing & Upwork Freelance Suite

Automated tools and strategy for hitting the **$1,000 Milestone** on Upwork using AI automation, web scrapers, and Telegram bots.

## 📁 Project Structure
- `config.json` - Telegram Bot credentials and user chat ID.
- `telegram_notifier.py` - Helper module to send messages and alerts to Telegram.
- `bot_listener.py` - Background daemon listening for your commands directly in Telegram.
- `proposal_generator.py` - Generates high-converting Upwork proposals and client outreach DMs.
- `UPWORK_STRATEGY.md` - Complete in-depth roadmap to secure $1,000+ in freelance earnings.

## 🤖 Using Your Telegram Bot (@Antrigravityroni_bot)
You can message your bot directly on Telegram from your phone:
- `/proposal <job description>` — Instantly generates a customized proposal draft.
- `/dm <name> <industry>` — Generates a direct outreach message.
- `/status` — Checks if your system is online.
- Text any message or question, and the bot will reply and log it.

## 🚀 Quick Commands
```bash
# Send a notification message to your Telegram:
python telegram_notifier.py "Your message here"

# Generate a proposal from the command line:
python proposal_generator.py "Client wants a Telegram bot with Python"

# Run the interactive Telegram listener:
python bot_listener.py
```
