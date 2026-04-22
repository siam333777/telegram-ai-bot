# Telegram AI Chatbot (Powered by Groq + LLaMA 3)

A simple Telegram bot that uses Groq's free AI API to answer messages. Each user gets their own chat history, so it remembers context within a conversation.

---

## Step 1 — Get your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. "My AI Bot") and a username (e.g. `myai_bot`)
4. BotFather will give you a **token** like: `123456789:ABCdef...`
5. Save it — this is your `TELEGRAM_TOKEN`

---

## Step 2 — Get your Groq API Key

1. Go to https://console.groq.com
2. Sign up for free
3. Click **"API Keys"** → **"Create API Key"**
4. Copy the key — this is your `GROQ_API_KEY`

> Groq's free tier is very generous — great for personal bots!

---

## Step 3 — Deploy to Railway

1. Go to https://railway.app and sign up (free)
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Push these files to a GitHub repo first
4. After linking the repo, go to your project → **Variables** tab
5. Add these two environment variables:
   - `TELEGRAM_TOKEN` → your token from Step 1
   - `GROQ_API_KEY` → your key from Step 2
6. Railway will auto-deploy. Your bot will start running!

---

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main bot code |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway how to run the bot |
| `runtime.txt` | Pins Python version to 3.11 |

---

## Bot Commands

| Command | What it does |
|---------|-------------|
| `/start` | Shows welcome message |
| `/reset` | Clears chat history for that user |
