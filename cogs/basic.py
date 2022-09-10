import discord
import logging

# Initialise logging.
logging.basicConfig(filename = 'logs/basic.log', encoding = 'utf-8', format = '%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)

# Bot version
version = "2.0.0-alpha3"

# New - The Cog class must extend the commands.Cog class
class Basic(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
   
    # Define a new command
    @discord.slash_command(name = 'help', description = 'Learn how to be a weeb.')
    async def help(self, ctx):
        # The third parameter comes into play when only one word argument has to be passed by the user
        # Prepare the embed
        help_embed = discord.Embed(
            title = 'Help',
            description = f"*Bot version: {version}*\n",
            color = discord.Colour.blurple()
        )

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
                inline = False
            )
        
        help_embed.add_field(
            name = '\u200b',
            value = "Type `/<command name>` to learn more and try it out!",
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
