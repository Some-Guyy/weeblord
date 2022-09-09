import discord
import nltk
import os
from dotenv import load_dotenv

load_dotenv() # Load all the variables from the env file.

# Check if nltk resources are downloaded on the machine, if not download them.
nltk_resources = [('tokenizers/punkt', 'punkt'), ('corpora/wordnet.zip', 'wordnet'), ('corpora/treebank.zip', 'treebank'), ('corpora/omw-1.4.zip', 'omw-1.4')]
for resource in nltk_resources:
    try:
        nltk.data.find(resource[0])
    except LookupError:
        nltk.download(resource[1])

# Allow bot to read message contents in guilds.
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(debug_guilds=[275926238504419328], intents = intents)

cogs_list = ['basic', 'fun']

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('TOKEN'))
