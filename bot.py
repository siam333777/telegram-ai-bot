import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# --- Setup ---
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# Stores conversation history per user
chat_histories = {}


# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm an AI assistant powered by Google Gemini.\n\n"
        "Just send me any message and I'll reply!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/reset - Clear chat history"
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
        chat_histories[user_id] = []

    # Add user message to history
    chat_histories[user_id].append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    try:
        await update.message.chat.send_action("typing")

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=chat_histories[user_id]
        )

        reply = response.text

        # Add assistant reply to history
        chat_histories[user_id].append(
            types.Content(role="model", parts=[types.Part(text=reply)])
        )

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
    
