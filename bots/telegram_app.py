# bots/telegram_app.py
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from core.message_handler import handle_ask_command, handle_image_upload, handle_summarize_command

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the help menu and instructions."""
    help_text = (
        "🤖 **Welcome to the Hybrid Company Bot!**\n\n"
        "Here is what I can do:\n"
        "🔹 `/ask <your question>` - Ask a question about company policies (RAG).\n"
        "🔹 `/summarize` - Get a summary of our recent conversation.\n"
        "🔹 **Send a Photo** - Upload any image, and I will describe it and generate tags."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /ask command and passes it to the Core Engine."""
    user_id = str(update.message.from_user.id)
    
    # context.args is a list of the words after /ask. We join them into a single string.
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Please provide a query! Example: `/ask How many sick days do I get?`", parse_mode='Markdown')
        return

    #Show a "typing..." status while Ollama generates the answer
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Hand off to the core/message_handler.py
    response = await handle_ask_command("telegram", user_id, query)
    
    await update.message.reply_text(response)

async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /summarize command."""
    user_id = str(update.message.from_user.id)
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Hand off to the brain!
    response = await handle_summarize_command("telegram", user_id)
    
    await update.message.reply_text(response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catches any photo uploaded by the user, downloads it, and passes it to Vision."""
    user_id = str(update.message.from_user.id)
    
    await update.message.reply_text("🖼️ Image received! Let me analyze that for you...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Telegram sends multiple sizes of the image. [-1] is the highest resolution.
    photo_file = await update.message.photo[-1].get_file()
    
    # Create a temporary directory to store the downloaded image
    os.makedirs("temp", exist_ok=True)
    temp_path = f"temp/tg_{user_id}.jpg"
    
    # Download the file from Telegram's servers to your local machine
    await photo_file.download_to_drive(custom_path=temp_path)
    
    # Hand off to the visual brain!
    response = await handle_image_upload("telegram", user_id, temp_path)
    
    # Clean up: Delete the image so your hard drive doesn't fill up over time
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    await update.message.reply_text(response)

def get_telegram_app(token: str):
    """
    Builds the Telegram Application. 
    We expose this function so main.py can grab the app and run it concurrently with Discord.
    """
    app = Application.builder().token(token).build()
    
    # Register the commands
    app.add_handler(CommandHandler("start", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("summarize", summarize_command))
    
    # Register the photo handler (triggers anytime an image is sent, no command needed)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    return app