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

Always format your responses using Telegram HTML formatting:
- Use <b>bold</b> for important words or headings
- Use <i>italic</i> for emphasis
- Use <u>underline</u> for key terms
- Use <code>monospace</code> for code, commands, or technical terms
- Use <pre>code block</pre> for multi-line code
- Use <blockquote>text</blockquote> for quotes or highlights
- Use <tg-spoiler>text</tg-spoiler> for spoilers or hidden info
- Use <a href="URL">link text</a> for links

Make responses well-structured, clear, and visually appealing using these formats naturally.
Never use markdown like **bold** or _italic_ — only use the HTML tags above."""


# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm an AI assistant powered by Groq + LLaMA 3.\n\n"
        "Just send me any message and I'll reply!\n\n"
        "<b>Commands:</b>\n"
        "/start - Show this message\n"
        "/reset - Clear chat history",
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

        # Try sending with HTML formatting
        try:
            await update.message.reply_text(reply, parse_mode="HTML")
        except Exception:
            # If HTML parsing fails, send as plain text
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
    
