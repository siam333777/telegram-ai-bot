import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- Setup ---
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

chat_histories = {}

SYSTEM_PROMPT = """You are a helpful and friendly AI assistant on Telegram.

Format your responses clearly and structured using these Telegram HTML tags:

FORMATTING RULES:
- <b>bold</b> — use ONLY for section headings or the most critical keyword (max 1-2 per response)
- <i>italic</i> — use ONLY for definitions or introducing a new term (not random emphasis)
- <code>monospace</code> — use ONLY for actual code, commands, file names, or technical syntax
- <pre>code block</pre> — use ONLY for multi-line code snippets
- <blockquote>text</blockquote> — use ONLY for quoting something or a key takeaway at the end
- <u>underline</u> — do NOT use at all
- <tg-spoiler>text</tg-spoiler> — use ONLY when explicitly asked
- <a href="URL">link text</a> — ALWAYS use this for any URL. Never show raw links. Example: <a href="https://wikipedia.org">Wikipedia</a>

STRUCTURE RULES:
- For explanations: start with a one-line summary, then use sections with <b>headings</b>
- For lists: use a clean emoji bullet like • or numbers
- Keep paragraphs short (2-3 sentences max)
- End with a helpful follow-up question or tip when relevant

NEVER randomly apply formatting to normal words. Less is more."""


# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm an AI assistant powered by Groq + LLaMA 3.\n\n"
        "Just send me any message and I'll reply!\n\n"
        "<b>Commands:</b>\n"
        "• /start — Show this message\n"
        "• /reset — Clear chat history",
        parse_mode="HTML"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    await update.message.reply_text("🔄 Chat history cleared! Let's start fresh.")


# --- Message Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    chat_histories[user_id].append({"role": "user", "content": user_message})

    try:
        await update.message.chat.send_action("typing")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[user_id],
            max_tokens=1024
        )

        reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": reply})

        try:
            await update.message.reply_text(reply, parse_mode="HTML")
        except Exception:
            await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error for user {user_id}: {e}")
        await update.message.reply_text(
            "⚠️ Something went wrong. Please try again or use /reset to start over."
        )


# --- Run the bot ---

if __name__ == "__main__":
    print("Bot is starting...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running! Press Ctrl+C to stop.")
    app.run_polling()
    
