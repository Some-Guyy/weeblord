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

cogs = ['cogs.basic']

@bot.event
async def on_ready():
    print(f"{info} Weeblord has risen!")
    print(f"{info} {datetime.now()}")
    for cog in cogs:
        bot.load_extension(cog)
    return

# @bot.command()
# async def help(ctx):
#     await ctx.send("No I don't care about you.")

# @bot.command()
# async def add(ctx, a: int, b: int):
#     await ctx.send(a+b)

# @bot.command()
# async def multiply(ctx, a: int, b: int):
#     await ctx.send(a*b)

# @bot.command()
# async def greet(ctx):
#     await ctx.send(":smiley: :wave: Hello, there!")

# @bot.command()
# async def cat(ctx):
#     await ctx.send("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif")

bot.run(token, bot = True, reconnect = True)