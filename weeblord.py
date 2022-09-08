import discord
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = discord.Bot(debug_guilds=[275926238504419328])

cogs_list = ['basic']

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('TOKEN')) # run the bot with the token
