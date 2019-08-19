import discord
from discord.ext import commands
from datetime import datetime

# Bot version
version = "0.2.0"

# These color constants are taken from discord.js library
colors = {
  'DEFAULT': 0x000000,
  'WHITE': 0xFFFFFF,
  'AQUA': 0x1ABC9C,
  'GREEN': 0x2ECC71,
  'BLUE': 0x3498DB,
  'PURPLE': 0x9B59B6,
  'LUMINOUS_VIVID_PINK': 0xE91E63,
  'GOLD': 0xF1C40F,
  'ORANGE': 0xE67E22,
  'RED': 0xE74C3C,
  'GREY': 0x95A5A6,
  'NAVY': 0x34495E,
  'DARK_AQUA': 0x11806A,
  'DARK_GREEN': 0x1F8B4C,
  'DARK_BLUE': 0x206694,
  'DARK_PURPLE': 0x71368A,
  'DARK_VIVID_PINK': 0xAD1457,
  'DARK_GOLD': 0xC27C0E,
  'DARK_ORANGE': 0xA84300,
  'DARK_RED': 0x992D22,
  'DARK_GREY': 0x979C9F,
  'DARKER_GREY': 0x7F8C8D,
  'LIGHT_GREY': 0xBCC0C0,
  'DARK_NAVY': 0x2C3E50,
  'BLURPLE': 0x7289DA,
  'GREYPLE': 0x99AAB5,
  'DARK_BUT_NOT_BLACK': 0x2C2F33,
  'NOT_QUITE_BLACK': 0x23272A
}

# New - The Cog class must extend the commands.Cog class
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Define a new command
    @commands.command(
        name = 'help',
        description = "The help command!",
        aliases = ['commands', 'command']
    )
    async def help_command(self, ctx, command='all'):
        # The third parameter comes into play when only one word argument has to be passed by the user
        # Prepare the embed
        help_embed = discord.Embed(
            title = 'Help',
            color = colors['PURPLE']
        )

        # Get a list of all cogs
        cogs = [c for c in self.bot.cogs.keys()]
        help_embed.description = f"*Bot version: {version}*\n"

        # If cog is not specified by the user, we list all cogs and commands
        if command == 'all':
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
        description = "To check if I'm alive.",
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


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file