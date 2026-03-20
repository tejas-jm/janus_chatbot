# bots/discord_app.py
import os
import discord
from discord.ext import commands
from core.message_handler import handle_ask_command, handle_image_upload, handle_summarize_command

# Set up Discord intents (required by Discord's API to read message content)
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot with the '/' prefix to match Telegram's UX
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'🟢 Discord bot is online and logged in as {bot.user}')

@bot.command(name='help')
async def help_command(ctx):
    """Displays the help menu and instructions."""
    help_text = (
        "🤖 **Welcome to the Hybrid Company Bot!**\n\n"
        "Here is what I can do:\n"
        "🔹 `/ask <your question>` - Ask a question about company policies (RAG).\n"
        "🔹 `/summarize` - Get a summary of our recent conversation.\n"
        "🔹 `/image` - Attach an image to this command, and I will describe it and generate tags."
    )
    await ctx.send(help_text)

@bot.command(name='ask')
async def ask_command(ctx, *, query: str = None):
    """Handles the /ask command and passes it to the Core Engine."""
    if not query:
        await ctx.send("Please provide a query! Example: `/ask What is the remote work policy?`")
        return

    user_id = str(ctx.author.id)
    
    # Show a typing indicator so the user knows the bot is thinking
    async with ctx.typing():
        # Hand off to the brain!
        response = await handle_ask_command("discord", user_id, query)
        
    await ctx.send(response)

@bot.command(name='summarize')
async def summarize_command(ctx):
    """Handles the /summarize command."""
    user_id = str(ctx.author.id)
    
    async with ctx.typing():
        # Hand off to the brain!
        response = await handle_summarize_command("discord", user_id)
        
    await ctx.send(response)

@bot.command(name='image')
async def image_command(ctx):
    """Catches an image attached to the /image command, downloads it, and passes it to Vision."""
    # Check if the user actually attached a file
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach an image file when using the `/image` command!")
        return

    attachment = ctx.message.attachments[0]
    
    # Basic validation to ensure it's an image
    if not attachment.content_type.startswith('image/'):
        await ctx.send("❌ The attached file doesn't look like an image. Please upload a valid picture.")
        return

    user_id = str(ctx.author.id)
    await ctx.send("🖼️ Image received! Let me analyze that for you...")
    
    async with ctx.typing():
        # Create a temporary directory to store the downloaded image
        os.makedirs("temp", exist_ok=True)
        temp_path = f"temp/dc_{user_id}_{attachment.filename}"
        
        # Download the file from Discord's servers to your local machine
        await attachment.save(temp_path)
        
        # Hand off to the visual brain!
        response = await handle_image_upload("discord", user_id, temp_path)
        
        # Clean up: Delete the image to save disk space
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    await ctx.send(response)

def get_discord_bot():
    """
    Exposes the bot instance so main.py can grab it and run it 
    concurrently alongside Telegram.
    """
    return bot