import discord
from discord.ext import commands

import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'rps',
        description = "Rock, Paper, Scissors!"
    )
    async def rps_command(self, ctx, choice = 'none'):
        if choice == 'none':
            await ctx.send(content = f"To use this command, type `{ctx.prefix}rps <choice>`\nChoices: `r/rock, p/paper, s/scissors`")
        else:
            def rps_sesh(player1, player2):
                none = []
                rocks = []
                for i in [player1, player2]:
                    if i[1] == 'rock':
                        rocks.append(i)
                    else:
                        none.append(i)
                if len(rocks) == 2:
                    return 'draw'
                elif len(rocks) == 1:
                    if none[0][1] == 'scissors':
                        return rocks[0][0]
                    else:
                        return none[0][0]
                else:
                    none = []
                    paper = []
                    for i in [player1, player2]:
                        if i[1] == 'paper':
                            paper.append(i)
                        else:
                            none.append(i)
                    if len(paper) == 2:
                        return 'draw'
                    elif len(paper) == 1:
                        return none[0][0]
                    else:
                        return 'draw'
            
            option_aliases = ['r', 'p', 's']
            options = ['rock', 'paper', 'scissors']
            option_emoji = [':new_moon:', ':newspaper:', ':scissors:'] # For discord emoji
            if choice.lower() not in option_aliases and choice.lower() not in options:
                await ctx.send(content = f"Wrong command bro, what the heck is {ctx.message.author}?")
                return
            elif choice.lower() in option_aliases:
                player = (ctx.message.author.name, options[option_aliases.index(choice.lower())])
            else:
                player = (ctx.message.author.name, choice.lower())
            
            cpu = (self.bot.user.name, options[random.randrange(len(options))])
            await ctx.send(content = f"{ctx.message.author.name} used {option_emoji[options.index(player[1])]}")
            await ctx.send(content = f"{self.bot.user.name} used {option_emoji[options.index(cpu[1])]}")
            
            if rps_sesh(player, cpu) == 'draw':
                await ctx.send(content = "Draw!")
            else:
                await ctx.send(content = f"{rps_sesh(player, cpu)} wins!")


def setup(bot):
    bot.add_cog(Fun(bot))