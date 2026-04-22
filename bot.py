import os
import re
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

SYSTEM_PROMPT = """You are WoniBot, a smart AI assistant on Telegram.

You MUST always format every response like a Telegram post. Follow these rules strictly:

1. ALWAYS start with a bold title or bold answer using <b>title</b>
2. Use <b>bold</b> for the direct answer, section headings, and key terms
3. Use <i>italic</i> for extra context, side notes, dates, names
4. Use <code>monospace</code> for code, commands, technical terms only
5. Use bullet points with • for lists
6. Use <a href="URL">text</a> for any links — NEVER show raw URLs
7. End every response with a follow-up question or tip in italic
8. Keep responses concise and well spaced

EXAMPLE of a good response to "What is AI?":

<b>Artificial Intelligence (AI)</b>

AI refers to machines that simulate human intelligence.

<b>Key Types:</b>
• <b>Narrow AI</b> — designed for one task
• <b>General AI</b> — human-level thinking
• <b>Super AI</b> — surpasses human intelligence

<i>AI is used in healthcare, finance, education, and more.</i>

<i>Would you like to know how AI is trained? 🤔</i>

IMPORTANT: Only use HTML tags like <b>, <i>, <code>. NEVER use markdown like **bold** or _italic_."""


def md_to_html(text):
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* or _italic_ to <i>italic</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    # Convert `code` to <code>code</code>
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Hi! I'm Wonibot</b>\n"
        "Your AI assistant powered by Groq + LLaMA 3.\n\n"
        "Just send me any message and I'll reply!\n\n"
        "<b>Commands:</b>\n"
        "• /start — Show this message\n"
        "• /reset — Clear chat history\n\n"
        "<i>📢 Follow us: @Woni_ai</i>",
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

        # Convert any markdown to HTML
        reply = md_to_html(reply)

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
   
