import discord
from discord.ext import commands

from datetime import datetime
import asyncio

# Bot version
version = "0.5.7"

# New - The Cog class must extend the commands.Cog class
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # The main error handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound, commands.UserInputError)
        
        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)
        
        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"`{ctx.prefix}{ctx.command}` has been disabled.")

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.author.send(f"Hmmm {ctx.message.author.name}? ...nope, don't remember you at all. Sorry, I don't speak to strangers.")
        
        elif isinstance(error, commands.PrivateMessageOnly):
            return await ctx.author.send(f"*Hush hush! PM me about it...*")

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                return await ctx.send("I couldn't find whoever that is. Are you sure they even exist?")

        # All other Errors not returned come here... And we can just print the default TraceBack.
        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    # Define a new command
    @commands.command(
        name = 'help',
        description = "Ay dood what do you think this command is for?",
        aliases = ['h', 'commands', 'command']
    )
    @commands.guild_only()
    async def help_command(self, ctx, command='all'):
        # Show that the bot is typing until a message is sent
        await ctx.channel.trigger_typing()

        # The third parameter comes into play when only one word argument has to be passed by the user
        # Prepare the embed
        help_embed = discord.Embed(
            title = 'Help',
            description = f"*Bot version: {version}*\n",
            color = 0x9B59B6 # PURPLE
        )

        # Get a list of all cogs
        cogs = [c for c in self.bot.cogs.keys()]

        # If cog is not specified by the user, we list all cogs and commands
        if command == 'all':
            help_embed.add_field(
                name = '\u200b',
                value = "__**Below are the categories and each command that it contains:**__",
                inline = False
            )

            for cog in cogs:
                # Get a list of all commands under each cog
                cog_commands = self.bot.get_cog(cog).get_commands()
                commands_list = ""
                for comm in cog_commands:
                    commands_list += f"{comm.name}\n"

                help_embed.add_field(
                    name = cog,
                    value = commands_list,
                    inline = False
                )
            
            help_embed.add_field(
                name = '\u200b',
                value = f"To learn more about a specific command, use `{ctx.prefix}help <command>`.",
                inline = False
            )

            await ctx.send(embed = help_embed)
            return
        else:
            for cog in cogs:
                cog_commands = self.bot.get_cog(cog).get_commands()
                for comm in cog_commands:
                    if command == comm.name:
                        help_text = f"**Command:** {comm.name}\n\n"
                        help_text += comm.description

                        if len(comm.aliases) > 0:
                            help_text += f"\n\n**Aliases:** `{'`, `'.join(comm.aliases)}`"

                        help_embed.description += f"\n{help_text}"
                        await ctx.send(embed = help_embed)
                        return

        # Notify the user of invalid command and finish the command
        await ctx.send('Invalid command specified.\nUse `help` command to list all command.')

    @commands.command(
        name = 'ping',
        description = "To check if I'm still alive.",
        aliases = ['p']
    )
    async def ping_command(self, ctx):
        start = datetime.timestamp(datetime.now())
        # Gets the timestamp when the command was used

        msg = await ctx.send(content="Pong!")
        # Sends a message to the user in the channel the message with the command was received.
        # Notifies the user that pinging has started

        await msg.edit(content=f"Pong! `{round((datetime.timestamp(datetime.now()) - start) * 1000)}ms`")
        # Ping completed and round-trip duration show in ms
        # Since it takes a while to send the messages
        # it will calculate how much time it takes to edit an message.
        # It depends usually on your internet connection speed
    
    @commands.command(
        name = 'roll',
        description = "The basic roll command. Every discord bot should have this, right? Choose a number and I'll roll a random number up to your chosen one.",
        aliases = ['r']
    )
    @commands.guild_only()
    async def roll_command(self, ctx, roll_amount = 'none'):
        await ctx.channel.trigger_typing()

        if roll_amount == 'none':
            await ctx.send(content = f"To use this command, type `{ctx.prefix}roll <number>`\nI'll roll a die of that many sides for you.")
        else:
            try:
                roll_amount = int(roll_amount)
                if roll_amount > 500:
                    await asyncio.sleep(3)
                    await ctx.send(content = "Oops, I ran out of dice to roll...")
                    return

                roll_text = ""
                if roll_amount == 0:
                    roll_text += "_ _"
                elif roll_amount < 0:
                    for i in range(abs(roll_amount)):
                        roll_text += "llor"
                else:
                    for i in range(roll_amount):
                        roll_text += "roll"

                await ctx.send(content = roll_text)

            except ValueError:
                await ctx.send(content = "Use whole numbers only dude, I don't have magical dice in here!")


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file