import discord
from discord.ext import commands

import random
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name = 'uwu-ify',
        description = "Uwu-ify de pwevious message. UwU",
        aliases = ['uwu']
    )
    @commands.guild_only()
    async def uwu_command(self, ctx):
        await ctx.channel.trigger_typing()

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
            string += " uwu"
            return string

        messages = await ctx.channel.history(limit = 2).flatten()
        message = messages[1]
        text = message.content

        uwu_embed = discord.Embed(
            description = uwu(text),
            color = 0xE91E63 # LUMINOUS_VIVID_PINK
        )
        uwu_embed.set_author(
            name = message.author.display_name,
            icon_url = message.author.avatar_url
        )
        await ctx.send(embed = uwu_embed)

    @commands.command(
        name = 'thesaurize',
        description = "Replace every word from the previous message into another word with a similar meaning. *(hopefully)*",
        aliases = ['tsr']
    )
    @commands.guild_only()
    async def thesaurize_command(self, ctx):
        await ctx.channel.trigger_typing()

        def thesaurize(input_string):
            tokenized_list = word_tokenize(input_string.lower())
            thesaurized_list = []
            for word in tokenized_list:
                synset_list = wordnet.synsets(word)
                thesaurized_word = word
                try_count = 0
                while thesaurized_word.lower() == word.lower():
                    try_count += 1
                    if try_count == 21:
                        break
                    if len(word) < 3:
                        break
                    if len(synset_list) > 0:
                        usable_synset_list = []
                        for synset in synset_list:
                            if len(synset.lemmas()) > 1:
                                usable_synset_list.append(synset)
                        if len(usable_synset_list) > 0:
                            thesaurized_word = random.choice(random.choice(usable_synset_list).lemmas()).name()
                        else:
                            break
                    else:
                        break
                thesaurized_list.append(thesaurized_word)
            return TreebankWordDetokenizer().detokenize(thesaurized_list)

        messages = await ctx.channel.history(limit = 2).flatten()
        message = messages[1]
        text = message.content

        tsr_embed = discord.Embed(
            description = thesaurize(text),
            color = 0x11806A # DARK_AQUA
        )
        tsr_embed.set_author(
            name = message.author.display_name,
            icon_url = message.author.avatar_url
        )
        await ctx.send(embed = tsr_embed)


def setup(bot):
    bot.add_cog(Fun(bot))