import discord
import logging
import nltk
import os
from dotenv import load_dotenv

# Create appdata directory if it doesn't exist.
if not os.path.exists("./appdata"):
    os.makedirs("./appdata")

# Initialise logging.
logging.basicConfig(filename = 'appdata/weeblord.log', encoding = 'utf-8', format = '%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)

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

if os.getenv('DEBUG_GUILDS') == None:
    bot = discord.Bot(intents = intents, activity = discord.Game(name = "( ͡° ͜ʖ ͡°) | /help"))
else:
    guilds = list(os.getenv('DEBUG_GUILDS').split(','))
    bot = discord.Bot(debug_guilds = guilds, intents = intents, activity = discord.Game(name = "( ͡° ͜ʖ ͡°) | /help"))

cogs_list = ['basic', 'fun', 'games']

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

@bot.event
async def on_ready():
    startup_message = f"{bot.user} is ready and online!"
    logging.info(startup_message)
    print(startup_message)

bot.run(os.getenv('TOKEN'))
