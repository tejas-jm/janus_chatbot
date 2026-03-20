import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Import our platform-specific bot initializers
from bots.telegram_app import get_telegram_app
from bots.discord_app import get_discord_bot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# Set up basic logging so we can see errors in the console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In a production environment, you would use python-dotenv or environment variables.
# For this assignment, you can paste your tokens directly here for testing.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "YOUR_DISCORD_TOKEN_HERE")

async def run_bots():
    """
    Initializes and runs both the Telegram and Discord bots concurrently 
    on the same event loop.
    """
    print("🚀 Starting Hybrid Bot Engine...")

    # 1. Initialize Telegram
    # We use the lower-level start() and start_polling() methods so it 
    # doesn't block the thread (unlike run_polling()).
    telegram_app = get_telegram_app(TELEGRAM_TOKEN)
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    print("🟢 Telegram bot is online and polling!")

    # 2. Initialize Discord
    # discord.py's start() method runs continuously, so we await it last.
    discord_bot = get_discord_bot()
    print("🟢 Starting Discord connection...")
    
    try:
        await discord_bot.start(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Discord Bot Error: {e}")
        print("Make sure your Discord token is correct and Message Content intents are enabled.")

if __name__ == "__main__":
    # Standard check to prevent running if imported elsewhere
    try:
        # Launch the async event loop
        asyncio.run(run_bots())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down bots manually...")