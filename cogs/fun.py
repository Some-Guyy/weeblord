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
            
            rps_embed = discord.Embed(
                title = 'Rock, Paper, Scissors!',
                description = f"{ctx.message.author.name} used {option_emoji[options.index(player[1])]}!\n{self.bot.user.name} used {option_emoji[options.index(cpu[1])]}!\n\n"
            )

            if rps_sesh(player, cpu) == 'draw':
                rps_embed.description += "It's a Draw!"
                rps_embed.color = 0xF1C40F # GOLD
            elif rps_sesh(player, cpu) == self.bot.user.name:
                rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
                rps_embed.color = 0xE74C3C # RED
                rps_embed.set_thumbnail(url = self.bot.user.avatar_url)
            else:
                rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
                rps_embed.color = 0x2ECC71 # GREEN
                rps_embed.set_thumbnail(url = ctx.message.author.avatar_url)

            await ctx.send(embed = rps_embed)

    @commands.command(
        name = 'uwu-ify',
        description = "Uwu-ify the previous message UwU",
        aliases = ['uwu']
    )
    async def uwu_command(self, ctx):
        def uwu(string):
            string = string.replace('l', 'w')
            string = string.replace('L', 'W')
            string = string.replace('r', 'w')
            string = string.replace('R', 'W')
            string = string.replace('thr', 'fw')
            string = string.replace('Thr', 'Fw')
            string = string.replace('THr', 'Fw')
            string = string.replace('THR', 'FW')
            string = string.replace('tHR', 'fW')
            string = string.replace('thR', 'fW')
            string = string.replace('th', 'd')
            string = string.replace('Th', 'D')
            string = string.replace('tH', 'D')
            string = string.replace('TH', 'D')
            string = string.replace('ou', 'uw')
            string = string.replace('Ou', 'Uw')
            string = string.replace('oU', 'uW')
            string = string.replace('OU', 'UW')
            return string

        messages = await ctx.channel.history(limit = 2).flatten()
        message = messages[1]
        text = message.content

        uwu_embed = discord.Embed(
            description = uwu(text),
            color = 0xE91E63 # LUMINOUS_VIVID_PINK
        )
        uwu_embed.set_author(
            name = message.author.name,
            icon_url = message.author.avatar_url
        )
        await ctx.send(embed = uwu_embed)


def setup(bot):
    bot.add_cog(Fun(bot))