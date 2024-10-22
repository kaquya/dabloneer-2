import sys
import discord
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from config.config_loader import BOT_TOKEN
from utils.logging_config import logger
from tasks.reset_tasks import reset_task_completions
from commands import balance, bank, shop, nominate

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Enable this if you need to access message content
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


# Global error handler
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Install exception handler
sys.excepthook = handle_exception

# Setup task scheduler
scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Zurich"))

# Schedule the daily reset at midnight
scheduler.add_job(
    reset_task_completions,
    CronTrigger(hour=0, minute=0),
    id="daily_reset",
    replace_existing=True,
    name="Daily task reset"
)

# Start the scheduler
scheduler.start()
logger.info("Scheduler started for task resets")

@bot.event
async def on_ready():
    await tree.sync(guild=None)
    logger.info(f"Logged in as {bot.user}")

# Load commands into the command tree
balance.setup_balance_command(tree, bot)
bank.setup_bank_commands(tree, bot)
shop.setup_shop_commands(tree, bot)
nominate.setup_nominate_commands(tree, bot)

# Run the bot
bot.run(BOT_TOKEN)
