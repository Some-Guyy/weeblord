import discord
from discord.ext import commands
import sys

from datetime import datetime
import traceback

# New - The Cog class must extend the commands.Cog class
class Error(commands.Cog):
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
        log_message = f"[ERROR] Invoked by: {ctx.message.author}\nServer and channel: {ctx.guild} - #{ctx.channel}\nTimestamp: {datetime.now()}\nIgnoring exception in command {ctx.prefix}{ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
        with open("../logs/weeblord.log", "a+") as f:
            f.write(f"\n{log_message}")
        print(log_message)


def setup(bot):
    bot.add_cog(Error(bot))