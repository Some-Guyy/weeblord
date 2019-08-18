import discord
from discord.ext import commands

import pickle
from datetime import datetime

f = open('../token/weeblord', 'rb')
token = pickle.load(f)
f.close()

info = '[INFO]'

bot = commands.Bot(
    command_prefix = '$',
    description = 'The lord of weebs.',
    case_insensitive = True
)

cogs = ['cogs.basic', 'cogs.fun']

@bot.event
async def on_ready():
    print(f"{info} Weeblord has risen!")
    print(f"{info} {datetime.now()}")
    # Remove the help command before loading the cogs
    bot.remove_command('help')
    for cog in cogs:
        bot.load_extension(cog)
    await bot.change_presence(activity = discord.Game("with myself ( ͡° ͜ʖ ͡°)"))
    return

bot.run(token, bot = True, reconnect = True)