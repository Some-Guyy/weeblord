import discord
import logging

import random
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

# Initialise logging.
logging.basicConfig(filename = 'logs/fun.log', encoding = 'utf-8', format = '%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)

class Fun(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name = 'uwu', description = "Uwu-ify the previous message.")
    @discord.option('text', description = "Uwu-ify a certain text instead.", required = False)
    async def uwu(self, ctx, text: str):
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

        if text == None:
            message = ctx.channel.last_message

            try:
                text = message.content
            except AttributeError:
                await ctx.respond("Previous message can't be uwu-ified")
                return
            
            uwu_embed = discord.Embed(
                description = uwu(text),
                color = discord.Colour.nitro_pink()
            )

            uwu_embed.set_author(
                name = message.author.display_name,
                icon_url = message.author.display_avatar
            )

            await ctx.respond(embed = uwu_embed)

        else:
            uwu_embed = discord.Embed(
                description = uwu(text),
                color = discord.Colour.nitro_pink()
            )

            uwu_embed.set_author(
                name = ctx.author.display_name,
                icon_url = ctx.author.display_avatar
            )

            await ctx.respond(embed = uwu_embed)

    @discord.slash_command(name = 'thesaurize', description = "Change each word of the previous message to a similar meaning.")
    @discord.option('text', description = "Thesaurize a certain text instead.", required = False)
    async def thesaurize(self, ctx, text: str):
        def thesaurize_string(input_string):
            skip_words = ['who'] # Add certain words that don't work too well.
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
                    if word.lower() in skip_words:
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
        
        if text == None:
            message = ctx.channel.last_message

            try:
                text = message.content
            except AttributeError:
                await ctx.respond("Previous message can't be thesaurized")
                return

            text = thesaurize_string(text)

            tsr_embed = discord.Embed(
                description = text,
                color = discord.Colour.og_blurple()
            )

            tsr_embed.set_author(
                name = message.author.display_name,
                icon_url = message.author.display_avatar
            )

            await ctx.respond(embed = tsr_embed)

        else:
            text = thesaurize_string(text)

            tsr_embed = discord.Embed(
                description = text,
                color = discord.Colour.og_blurple()
            )

            tsr_embed.set_author(
                name = ctx.author.display_name,
                icon_url = ctx.author.display_avatar
            )
            
            await ctx.respond(embed = tsr_embed)

def setup(bot):
    bot.add_cog(Fun(bot))
