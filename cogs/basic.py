import discord
import logging

logging.basicConfig(filename = 'appdata/weeblord.log', encoding = 'utf-8', format = '%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)

# Bot version
version = "2.0.9"

# New - The Cog class must extend the commands.Cog class
class Basic(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
   
    # Define a new command
    @discord.slash_command(name = 'help', description = 'Learn how to be a weeb.')
    async def help(self, ctx):
        libraries_dict = {
            "python-dotenv": "https://github.com/theskumar/python-dotenv",
            "nltk": "https://www.nltk.org/",
            "cinemagoer": "https://cinemagoer.github.io/"
        }

        # Prepare the embed
        help_embed = discord.Embed(
            title = 'Help',
            description = "What can I do for you?\n",
            color = discord.Colour.brand_green(),
        ).set_author(
            name = self.bot.user.display_name,
            icon_url = self.bot.user.display_avatar
        ).set_thumbnail(
            url = self.bot.user.display_avatar
        ).set_footer(text = f"v{version}")

        # Get a list of all cogs
        cogs = [c for c in self.bot.cogs.keys()]

        # We list all cogs and commands
        help_embed.add_field(
            name = '\u200b',
            value = "__**Below are the categories and each command that it contains**__",
            inline = False
        )

        for cog in cogs:
            # Get a list of all commands under each cog
            cog_commands = self.bot.get_cog(cog).get_commands()
            commands_list = ""

            for comm in cog_commands:
                commands_list += f"{comm.name}\n"
            
            # If cog has no commands, do not list it
            if commands_list == "":
                continue

            help_embed.add_field(
                name = cog,
                value = commands_list,
                inline = True
            )
        
        help_embed.add_field(
            name = '\u200b',
            value = "Go ahead and try one out with `/<command>`!\n\u200b",
            inline = False
        )

        # Acknowledgments
        libraries = ""
        for library in libraries_dict:
            libraries += f"\n[{library}]({libraries_dict[library]})"

        help_embed.add_field(
            name = 'Acknowledgements',
            value = f"This bot was created using [Pycord](https://pycord.dev/), together with other open source libraries!\n\u200b\n__Libraries__{libraries}\n\u200b",
            inline = False
        )

        await ctx.respond(embed = help_embed)

    @discord.slash_command(name = 'ping', description = "To check whether I'm still alive.")
    async def ping(self, ctx):
        await ctx.respond(f":ping_pong: Pong! {round(self.bot.latency * 1000)}ms")
    
    @discord.slash_command(name = 'roll', description = "Choose a number and I'll roll a random number from 0 to your number.")
    @discord.option('number', description = "How big you want your dice to be?")
    async def roll(self, ctx, number: int):
        number = int(number)

        if number > 500:
            await ctx.respond("Oops, I ran out of dice to roll...")
            return

        roll_text = ""

        if number == 0:
            roll_text += "_ _"
        elif number < 0:
            for i in range(abs(number)):
                roll_text += "llor"
        else:
            for i in range(number):
                roll_text += "roll"

        await ctx.respond(roll_text)

def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
