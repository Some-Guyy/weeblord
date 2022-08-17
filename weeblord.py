import discord
from discord.ext import commands

import nltk
import os
import pytz
from datetime import datetime, timezone

nltk.download('treebank')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Token that allows the bot to login
f = open('./token.txt', 'r')
token = f.read()
f.close()

# Prefix for the bot
f = open('./prefix.txt', 'r')
prefix = f.read()
f.close()

bot = commands.Bot(
    command_prefix = prefix,
    description = 'The lord of weebs.',
    case_insensitive = True
)

cogs = ['cogs.basic', 'cogs.error', 'cogs.fun', 'cogs.games']

@bot.event
async def on_ready():
    log_message = f"[START-UP] Weeblord has risen! Timestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    with open("./logs/weeblord.log", "a") as f:
        f.write(f"\n\n{log_message}")
    print(log_message)

    # Remove the help command before loading the cogs
    bot.remove_command('help')
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except commands.errors.ExtensionAlreadyLoaded:
            log_message = f"[INFO] Extension {cog} tried to load but is already loaded. This may be due to reconnection.\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a") as f:
                f.write(f"\n\n{log_message}")
            print(log_message)

    await bot.change_presence(activity = discord.Game(f"( ͡° ͜ʖ ͡°) | {prefix}help"))

bot.run(token, bot = True, reconnect = True)

# # These color constants are taken from discord.js library
# colors = {
#   'DEFAULT': 0x000000,
#   'WHITE': 0xFFFFFF,
#   'AQUA': 0x1ABC9C,
#   'GREEN': 0x2ECC71,
#   'BLUE': 0x3498DB,
#   'PURPLE': 0x9B59B6,
#   'LUMINOUS_VIVID_PINK': 0xE91E63,
#   'GOLD': 0xF1C40F,
#   'ORANGE': 0xE67E22,
#   'RED': 0xE74C3C,
#   'GREY': 0x95A5A6,
#   'NAVY': 0x34495E,
#   'DARK_AQUA': 0x11806A,
#   'DARK_GREEN': 0x1F8B4C,
#   'DARK_BLUE': 0x206694,
#   'DARK_PURPLE': 0x71368A,
#   'DARK_VIVID_PINK': 0xAD1457,
#   'DARK_GOLD': 0xC27C0E,
#   'DARK_ORANGE': 0xA84300,
#   'DARK_RED': 0x992D22,
#   'DARK_GREY': 0x979C9F,
#   'DARKER_GREY': 0x7F8C8D,
#   'LIGHT_GREY': 0xBCC0C0,
#   'DARK_NAVY': 0x2C3E50,
#   'BLURPLE': 0x7289DA,
#   'GREYPLE': 0x99AAB5,
#   'DARK_BUT_NOT_BLACK': 0x2C2F33,
#   'NOT_QUITE_BLACK': 0x23272A
# }

