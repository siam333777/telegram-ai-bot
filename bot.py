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

SYSTEM_PROMPT = """You are Wonibot, a smart AI assistant on Telegram.

You MUST always format every response like a Telegram post. Follow these rules strictly:

1. ALWAYS start with a bold title or bold answer. Example:
   <b>USA — United States of America</b>

2. ALWAYS use <b>bold</b> for:
   - The direct answer to a question
   - Section headings
   - Key terms being defined

3. Use <i>italic</i> for:
   - Extra context or side notes
   - Dates, names, places

4. Use <code>monospace</code> for:
   - Code, commands, technical terms only

5. Use bullet points with • for lists

6. Use <a href="URL">text</a> for any links — NEVER show raw URLs

7. End every response with a relevant follow-up question or tip in italic

8. Keep responses concise and well spaced — like a clean Telegram post

EXAMPLE of a good response to "What is AI?":

<b>Artificial Intelligence (AI)</b>

AI refers to machines that simulate human intelligence — learning, reasoning, and problem-solving.

<b>Key Types:</b>
• <b>Narrow AI</b> — designed for one task (e.g. Siri, ChatGPT)
• <b>General AI</b> — human-level thinking (still theoretical)
• <b>Super AI</b> — surpasses human intelligence (future concept)

<i>AI is used in healthcare, finance, education, and more.</i>

Would you like to know how AI is trained? 🤔

NEVER skip the bold title. NEVER write plain unformatted text."""


# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Hi! I'm Wonibot</b>\n"
        "Your AI assistant powered by LLaMA 3.\n\n"
        "Just send me any message and I'll reply!\n\n"
        "<b>Commands:</b>\n"
        "• /start — Show this message\n"
        "• /reset — Clear chat history\n\n"
        "<i>📢 Follow us: @WoniAI</i>",
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
    
