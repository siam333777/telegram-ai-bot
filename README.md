# Telegram AI Chatbot (Powered by Google Gemini)

A simple Telegram bot that uses Google Gemini to answer messages. Each user gets their own chat history, so it remembers context within a conversation.

---

## Step 1 — Get your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. "My AI Bot") and a username (e.g. `myai_bot`)
4. BotFather will give you a **token** like: `123456789:ABCdef...`
5. Save it — this is your `TELEGRAM_TOKEN`

---

## Step 2 — Get your Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key — this is your `GEMINI_API_KEY`

> The free tier gives you 15 requests/minute and 1 million tokens/day — plenty for a personal bot!

---

## Step 3 — Deploy to Railway

1. Go to https://railway.app and sign up (free)
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Push these files to a GitHub repo first (or use Railway's file upload)
4. After linking the repo, go to your project → **Variables** tab
5. Add these two environment variables:
   - `TELEGRAM_TOKEN` → your token from Step 1
   - `GEMINI_API_KEY` → your key from Step 2
6. Railway will auto-deploy. Your bot will start running!

---

## Files

| File | Purpose |
|------|---------|
| `bot.py` | Main bot code |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway how to run the bot |

---

## Bot Commands

| Command | What it does |
|---------|-------------|
| `/start` | Shows welcome message |
| `/reset` | Clears chat history for that user |

---

## How to push to GitHub (quick guide)

```bash
git init
git add .
git commit -m "Initial bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```
