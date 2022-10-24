import discord
from discord.ext import commands
import logging
import sys
import traceback
import asyncio

import random
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from difflib import SequenceMatcher
from imdb import Cinemagoer, IMDbError

logging.basicConfig(filename = 'appdata/weeblord.log', encoding = 'utf-8', format = '%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)

charge_timeout = 30
wm_timeout = 120

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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class Games(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = 'charge', description = "Challenge me to a game of charge! 'Help' to learn more.")
    @discord.option('option', description = "Use 'Help' to learn more.", choices = ['Help'], required = False)
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    async def charge(self, ctx, option: str):
        move_dict = {
            'charge': {'cost': -1, 'status': 'restore', 'stylized': ':zap:Charge', 'cost_info': "None", 'description': "+1 Mana"},
            'block': {'cost': 0, 'status': 'defence', 'stylized': ':shield:Block', 'cost_info': "None", 'description': "Blocks Bom & Slash"},
            'jump': {'cost': 0, 'status': 'defence', 'stylized': ':runner:Jump', 'cost_info': "None", 'description': "Dodges Bom & Boom"},
            'bom': {'cost': 1, 'status': 'attack', 'stylized': ':comet:Bom', 'cost_info': "1", 'description': "Level 1 Attack"},
            'boom': {'cost': 2, 'status': 'attack', 'stylized': ':boom:Boom', 'cost_info': "2", 'description': "Level 2 Attack"},
            'slash': {'cost': 2, 'status': 'attack', 'stylized': ':crossed_swords:Slash', 'cost_info': "2", 'description': "Level 2 Attack"},
            'smash': {'cost': 4, 'status': 'attack', 'stylized': ':wind_blowing_face:Smash', 'cost_info': "4", 'description': "Max Level Attack"},
            'giveup': {'cost': 0, 'status': 'dead', 'stylized': ':flag_white: Gave up', 'cost_info': "Your loss", 'description': "Give up!"}
        }

        if option == 'Help':
            # Help
            help_embed = discord.Embed(
                title = 'Charge!',
                description = f"Challenge me to a battle of wits and resources until one of us loses!\nYou have {charge_timeout} seconds to make a move.\nEach move has a different mana cost. During a match, use `c <move>` to use a move.",
                color = discord.Colour.blue()
            )

            move_names = ''
            move_costs = ''
            move_descriptions = ''

            for move in move_dict:
                move_names += f"{move}\n"
                move_costs += f"{move_dict[move]['cost_info']}\n"
                move_descriptions += f"{move_dict[move]['description']}\n"

            help_embed.add_field(name = 'Move', value = move_names, inline = True)
            help_embed.add_field(name = 'Cost', value = move_costs, inline = True)
            help_embed.add_field(name = 'Description', value = move_descriptions, inline = True)

            await ctx.respond(embed = help_embed)
            ctx.command.reset_cooldown(ctx)

        else:
            # Start game
            await ctx.respond(f"{ctx.author.display_name} started a Charge match!")

            class Player:
                def __init__(self, name):
                    self.name = name
                    self.mana = 1
                    self.status = 'standby'
                    self.move = ':zap:Charge'
                
                def use_move(self, move_name, cost):
                    self.move = move_dict[move_name]['stylized']
                    self.mana -= cost
                    self.power = cost
                    self.status = move_dict[move_name]['status']
                    if self.status == 'defence':
                        self.power = 2
                
                def die(self):
                    self.status = 'dead'

            def cpu_ai(player, cpu, move_dict):
                if cpu.mana == 4:
                    move = 'smash'
                elif player.mana == 0:
                    move = random.choice(list(move_dict))
                    while move == 'giveup' or cpu.mana - move_dict[move]['cost'] < 0 or move_dict[move]['status'] == 'defence':
                        move = random.choice(list(move_dict))
                else:
                    if random.randrange(100) < 20:
                        move = 'charge'
                    else:
                        move = random.choice(list(move_dict))
                        while move == 'giveup' or cpu.mana - move_dict[move]['cost'] < 0:
                            move = random.choice(list(move_dict))

                return move
                
            def announce(situation, winner, loser):
                # During non-winner/loser cases they will still be used in place of player1/player2 or charger/defender
                lines = {
                    'both_restore': [
                        f"The tension between them continues to rise...",
                        f"The tension betweeen them rises...",
                        f"The air thickens.",
                        f"An aura of power can be felt throughout the air.."
                    ],
                    'same_defend': [
                        f"Both of them {winner.move}ed! Nothing else happened.",
                        f"It's quiet...oh that's because both of them were {winner.move}ing...",
                        f"A {winner.move} from both of 'em! Are they too scared?"
                    ],
                    'diff_defend': [
                        f"{winner.name} {winner.move}ed while {loser.name} {loser.move}ed! Nothing else happened.",
                        f"{winner.name} {winner.move}ed and {loser.name} {loser.move}ed. What is this a performance?",
                        f"{winner.name} {winner.move}ed and {loser.name} {loser.move}ed. Who would make the first move?"
                    ],
                    'same_attack': [
                        f"The powers cancelled each other out!",
                        f"Both {winner.move}ed against the other with full power! They both still seem fine though.."
                    ],
                    'diff_attack': [
                        f"{winner.name} used {winner.move} but {loser.name} used {loser.move}! It's a draw!",
                        f"Ooh close! {winner.name}'s {winner.move} was just about as strong as {loser.name}'s {loser.move}"
                    ],
                    'restore_defend': [
                        f"Free mana for {winner.name}! All {loser.name} did was {loser.move}!",
                        f"{loser.name}, was that a charge too? Oh wait no that was a {loser.move}.",
                        f"{loser.name} defended with {loser.move} while {winner.name} charged! Nothing else happened."
                    ],
                    'attack_overpower': [
                        f"{winner.name} DESSIMATED {loser.name}'s {loser.move} with {winner.move}!",
                        f"{winner.name}'s {winner.move} broke {loser.name}'s {loser.move}!",
                        f"{winner.name} overpowered {loser.name}'s {loser.move} with {winner.move}!",
                        f"{loser.name} used {loser.move}. It doesn't matter though because {winner.name} used {winner.move}!!",
                        f"The {loser.move} by {loser.name} was no match for {winner.name}'s {winner.move}."
                    ],
                    'defend_overpower': [
                        f"{winner.name} managed to survive from {loser.name}'s {loser.move} with {winner.move}!",
                        f"{winner.name} easily dealt with {loser.name}'s {loser.move} by {winner.move}ing!",
                        f"{loser.name}'s {loser.move} was rendered useless by {winner.name}'s {winner.move}!"
                    ],
                    'give_up': [
                        f"{loser.name} {loser.move}! Easy win for {winner.name}!",
                        f"{loser.name} {loser.move}! What a bore!",
                        f"{winner.name} used {winner.move}! But wait! {loser.name} pulled up the white flag! :flag_white:"
                    ]
                }
                if situation in lines:
                    return random.choice(lines[situation])
                else:
                    logging.warning(f"No such situation called {situation}!")
                    return f"[ERROR] No such situation called {situation}!"
            
            def both_defend(player1, player2):
                if player1.move == player2.move:
                    return announce('same_defend', player, cpu)
                else:
                    return announce('diff_defend', player, cpu)
                    
            def charge_defend(player1, player2):
                if player1.status == 'restore':
                    charger = player1
                    defender = player2
                elif player2.status == 'restore':
                    charger = player2
                    defender = player1
                else:
                    player1.die()
                    player2.die()
                    logging.warning("Code should not reach here!")
                    return "[ERROR] Code should not reach here!"

                return announce('restore_defend', charger, defender)
            
            def defend_attack(player1, player2):
                if player1.status == 'defence':
                    defender = player1
                    attacker = player2
                else:
                    defender = player2
                    attacker = player1
                
                if attacker.power > defender.power:
                    defender.die()
                    return announce('attack_overpower', attacker, defender)
                elif attacker.power == defender.power:
                    if attacker.move == move_dict['boom']['stylized'] and defender.move == move_dict['jump']['stylized'] or attacker.move == move_dict['slash']['stylized'] and defender.move == move_dict['block']['stylized']:
                        return announce('defend_overpower', defender, attacker)
                    else:
                        defender.die()
                        return announce('attack_overpower', attacker, defender)
                elif attacker.power < defender.power:
                    return announce('defend_overpower', defender, attacker)
                else:
                    player1.die()
                    player2.die()
                    logging.warning("Code should not reach here!")
                    return "[ERROR] Code should not reach here!"
                    
            def attack_overpower(player1, player2):
                if player1.power > player2.power:
                    winner = player1
                    loser = player2
                elif player1.power < player2.power:
                    winner = player2
                    loser = player1
                else:
                    player1.die()
                    player2.die()
                    logging.warning("Code should not reach here!")
                    return "[ERROR] Code should not reach here!"
                loser.die()
                return announce('attack_overpower', winner, loser)

            # Define a check function that validates the message received by the bot
            def c_check(message: discord.Message):
                # Look for the message sent in the same channel where the command was used
                # As well as by the user who used the command.
                return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id and message.content.lower()[:2] == 'c '

            player = Player(ctx.author.display_name)
            cpu = Player(ctx.me.display_name)
            
            # Initialise embed
            charge_embed = discord.Embed(
                title = 'Charge!',
                description = f"{player.name} challenged {cpu.name} to a game of Charge!\n{player.name} used {player.move}!\n{cpu.name} used {cpu.move}!",
                color = discord.Colour.blue()
            )
            
            # Game until one player loses
            while player.status != 'dead' and cpu.status != 'dead':
                charge_embed.add_field(
                    name = '\u200b',
                    value = f"+-------------------------------+\n{player.name}'s :yin_yang:Mana: {player.mana}\n+-------------------------------+\n{cpu.name}'s :yin_yang:Mana: {cpu.mana}\n+-------------------------------+\n\n:warning:Remember to format your move like this: `c <move>`!\nNext move?",
                    inline = False
                )
                # Delete previous message
                if 'turn_message' in locals():
                    await turn_message.delete()
                turn_message = await ctx.send(embed = charge_embed)

                # CPU move
                cpu_move = cpu_ai(player, cpu, move_dict)

                # Player move
                valid = 'no'
                while valid == 'no':
                    try:
                        move_message = await self.bot.wait_for('message', check = c_check, timeout = charge_timeout)
                    except asyncio.TimeoutError:
                        logging.info(f"{ctx.author} took too long to respond during Charge in {ctx.guild} - #{ctx.channel}")
                        charge_embed = discord.Embed(
                            title = 'Charge!',
                            description = f"{ctx.author.display_name}, you took too long to respond!\n{self.bot.user.display_name} WINS! :tada:"
                        )

                        charge_embed.color = discord.Colour.red()
                        charge_embed.set_thumbnail(url = self.bot.user.display_avatar)
                        await ctx.send(embed = charge_embed)
                        ctx.command.reset_cooldown(ctx)
                        return

                    if move_message.content[:2].lower() == 'c ':
                        await ctx.channel.trigger_typing()
                        player_move = move_message.content[2:].lower()
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await move_message.delete()
                        valid = 'yes'

                if player_move == 'help':
                    charge_embed = discord.Embed(
                        title = 'Charge!',
                        description = "Aight there's yer movelist.",
                        color = discord.Colour.blue()
                    )

                    move_names = ''
                    move_costs = ''
                    move_descriptions = ''

                    for move in move_dict:
                        move_names += f"{move}\n"
                        move_costs += f"{move_dict[move]['cost_info']}\n"
                        move_descriptions += f"{move_dict[move]['description']}\n"

                    charge_embed.add_field(name = 'Move', value = move_names, inline = True)
                    charge_embed.add_field(name = 'Cost', value = move_costs, inline = True)
                    charge_embed.add_field(name = 'Description', value = move_descriptions, inline = True)
                    continue

                elif player_move not in move_dict:
                    charge_embed = discord.Embed(
                        title = 'Charge!',
                        description = f"What kind of move is {player_move}?!\nType `c help` to see the movelist.",
                        color = discord.Colour.blue()
                    )
                    continue
                elif player.mana - move_dict[player_move]['cost'] < 0:
                    charge_embed = discord.Embed(
                        title = 'Charge!',
                        description = "Not enough mana!",
                        color = discord.Colour.blue()
                    )
                    continue
                else:
                    player.use_move(player_move, move_dict[player_move]['cost'])
                    cpu.use_move(cpu_move, move_dict[cpu_move]['cost'])

                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = f"{player.name}: {player.move}\n{cpu.name}: {cpu.move}",
                    color = discord.Colour.blue()
                )
                
                # Fight commence!
                # Player gives up
                if player.move == ':flag_white: Gave up':
                    charge_embed.add_field(
                        name = '\u200b',
                        value = announce('give_up', cpu, player),
                        inline = False
                    )
                    player.status = 'dead'
                # Both charge
                elif player.status == cpu.status == 'restore':
                    charge_embed.add_field(
                        name = '\u200b',
                        value = announce('both_restore', player, cpu),
                        inline = False
                    )
                # Both defend
                elif player.status == cpu.status == 'defence':
                    charge_embed.add_field(
                        name = '\u200b',
                        value = both_defend(player, cpu),
                        inline = False
                    )
                # Both same attack power
                elif player.status == cpu.status == 'attack' and player.power == cpu.power:
                    if player.move != cpu.move:
                        charge_embed.add_field(
                            name = '\u200b',
                            value = announce('diff_attack', player, cpu),
                            inline = False
                        )
                    else:
                        charge_embed.add_field(
                            name = '\u200b',
                            value = announce('same_attack', player, cpu),
                            inline = False
                        )
                
                # Defend and charge
                elif player.status == 'restore' and cpu.status == 'defence' or cpu.status == 'restore' and player.status == 'defence':
                    charge_embed.add_field(
                        name = '\u200b',
                        value = charge_defend(player, cpu),
                        inline = False
                    )
                
                # Defend and attack
                elif player.status == 'defence' and cpu.status == 'attack' or player.status == 'attack' and cpu.status == 'defence':
                    charge_embed.add_field(
                        name = '\u200b',
                        value = defend_attack(player, cpu),
                        inline = False
                    )
                    
                # Overpowering attacks
                else:
                    charge_embed.add_field(
                        name = '\u200b',
                        value = attack_overpower(player, cpu),
                        inline = False
                    )
            # Delete previous message
            await turn_message.delete()

            if player.status == cpu.status == 'dead':
                logging.warning(f"Something wrong occurred during Charge with {ctx.author} in {ctx.guild} - #{ctx.channel}. Both dead.")
                await ctx.send("[ERROR] Something wrong occurred during the fight. Both dead.")

            elif player.status == 'dead':
                charge_embed.add_field(
                    name = '\u200b',
                    value = f"{cpu.name} WINS! :tada:",
                    inline = False
                )
                charge_embed.color = discord.Colour.red()
                charge_embed.set_thumbnail(url = self.bot.user.display_avatar)
                await ctx.send(embed = charge_embed)

            elif cpu.status == 'dead':
                charge_embed.add_field(
                    name = '\u200b',
                    value = f"{player.name} WINS! :tada:",
                    inline = False
                )
                charge_embed.color = discord.Colour.green()
                charge_embed.set_thumbnail(url = ctx.author.display_avatar)
                await ctx.send(embed = charge_embed)
                
            else:
                logging.warning(f"Something wrong occurred during Charge with {ctx.author} in {ctx.guild} - #{ctx.channel}. None of the players are dead.")
                await ctx.send("[ERROR] None of us are dead. Code should not have reached here.")
            
            ctx.command.reset_cooldown(ctx)
        
    @charge.error
    async def charge_handler(self, ctx, error):
        ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.CommandOnCooldown):
            logging.info(f"{ctx.author} tried to run {ctx.command} in {ctx.guild} - #{ctx.channel} while an instance is already running.")
            await ctx.respond(f"A game of {ctx.command} is already running on this channel!")

        else:
            log_message = f"Invoked by: {ctx.author}. During {ctx.command}. Server and channel: {ctx.guild} - #{ctx.channel}. Ignoring exception in command {ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            logging.warning(log_message)
            print("[ERROR] " + log_message)
            await ctx.send("An error has occurred! Check the logs for details.")

    @discord.slash_command(name = 'wm', description = "WhatMovie: Guess a random movie given a thesaurized plot!")
    @discord.option('category', description = "Category of movies. (Default: top)", choices = ['top', 'popular', 'shitty', 'marvel'], default = 'top')
    @discord.option('mode', description = "Freeplay(default): Play at your own pace. Party: Challenge others to score the most points!", choices = ['freeplay', 'party'], default = 'freeplay')
    @discord.option('win', description = "Only for party mode. Number of points required to win the game.", min_value = 1, max_value = 10, default = 'default')
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    async def what_movie(self, ctx, category: str, mode: str, win: int):
        def wm_check(message: discord.Message):
            # Look for the message sent in the same channel where the command was used
            return message.channel.id == ctx.channel.id and message.content.lower()[:3] == 'wm '

        def get_movie(category):
            ia = Cinemagoer()
            if category == 'top':
                top = ia.get_top250_movies()
                random_movie = top[random.randrange(0,len(top))]
                movie_id = random_movie.movieID
            
            elif category == 'popular':
                popular = ia.get_popular100_movies()
                random_movie = popular[random.randrange(0,len(popular))]
                movie_id = random_movie.movieID
            
            elif category == 'shitty':
                bottom = ia.get_bottom100_movies()
                random_movie = bottom[random.randrange(0,len(bottom))]
                movie_id = random_movie.movieID

            else:
                movie_id_list = random.choice(movie_dict[category]['id'])
                movie_id = movie_id_list[2:]

            movie = ia.get_movie(movie_id)
            movie_plot = movie['plot'][random.randrange(0, len(movie['plot']))]
            movie_plot = movie['plot'][random.randrange(0, len(movie['plot']))]
            thesaurized_plot = thesaurize_string(movie_plot)
            
            return movie, movie_id, thesaurized_plot
        
        what_movie_title = "What movie is this?"
        movie_dict = {
            'marvel': {
                'id': [ # List of titles are manually added from here: https://en.wikipedia.org/wiki/List_of_films_based_on_Marvel_Comics_publications
                    'tt0120611', 'tt0120903', 'tt0187738',
                    'tt0145487', 'tt0287978', 'tt0290334',
                    'tt0286716', 'tt0330793', 'tt0316654',
                    'tt0359013', 'tt0357277', 'tt0120667',
                    'tt0376994', 'tt0259324', 'tt0413300',
                    'tt0486576', 'tt0371746', 'tt0800080',
                    'tt0450314', 'tt0458525', 'tt1228705',
                    'tt0800369', 'tt1270798', 'tt0458339',
                    'tt1071875', 'tt0848228', 'tt0948470',
                    'tt1300854', 'tt1430132', 'tt1981115',
                    'tt1843866', 'tt1872181', 'tt1877832',
                    'tt2015381', 'tt2395427', 'tt0478970',
                    'tt1502712', 'tt1431045', 'tt3498820',
                    'tt3385516', 'tt1211837', 'tt3315342',
                    'tt3896198', 'tt2250912', 'tt3501632',
                    'tt1825683', 'tt4154756', 'tt5463162',
                    'tt5095030', 'tt1270797', 'tt4154664',
                    'tt4154796', 'tt6565702', 'tt6320628',
                    'tt2245084', 'tt4633694', 'tt4682266',
                    'tt3480822', 'tt9376612', 'tt7097896',
                    'tt9032400', 'tt10872600', 'tt5108870',
                    'tt9419884', 'tt10648342', 'tt9114286'
                    ]
            }
        }

        if mode == 'freeplay':
            what_movie_instructions = ":warning: Remember to FORMAT your message with `wm <guess>` when attempting to guess! Send `wm giveup` to give up and get a different movie, or `wm stop` to stop the session."

            while True:
                await ctx.respond("Hmmm which movie shall I choose? :thinking: Lemme see...")
                await ctx.channel.trigger_typing()

                movie, movie_id, thesaurized_plot = get_movie(category)

                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = f"Movie category: **{category}**",
                    color = discord.Colour.magenta()
                )

                # Split plot if its too long for embed fields.
                if len(thesaurized_plot) > 1000:
                    for i in range(-(len(thesaurized_plot) // -1000)):
                        if i == 0:
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"__**Plot**__\n{thesaurized_plot[:(i+1)*1000]}...",
                                inline = False
                            )
                        elif i-1 == -(len(thesaurized_plot) // -1000):
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"...{thesaurized_plot[i*1000:]}",
                                inline = False
                            )
                        else:
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"...{thesaurized_plot[i*1000:(i+1)*1000]}...",
                                inline = False
                            )
                else:
                    wm_embed.add_field(
                            name = '\u200b',
                            value = f"__**Plot**__\n{thesaurized_plot}",
                            inline = False
                        )
                
                wm_embed.add_field(
                    name = '\u200b',
                    value = what_movie_instructions,
                    inline = False
                )

                wm_message = await ctx.send(embed = wm_embed)
                guessed = 'no'

                while guessed == 'no':
                    try:
                        player_message = await self.bot.wait_for('message', check = wm_check, timeout = wm_timeout)
                    except asyncio.TimeoutError:
                        logging.info(f"No one responded for too long during {ctx.command} invoked by {ctx.author} in {ctx.guild} - #{ctx.channel}")
                        wm_embed = discord.Embed(
                            title = what_movie_title,
                            description = f"No one responded for too long. :shrug:\nGame over.\nThe movie was [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                            color = discord.Colour.red()
                        )
                        if movie['cover url'] is not None:
                            wm_embed.set_image(url = movie['cover url'])
                        await ctx.send(embed = wm_embed)
                        ctx.command.reset_cooldown(ctx)
                        return

                    player_last_guessed = player_message.author.display_name
                    player_guess = player_message.content[3:].lower()

                    if player_guess == 'giveup':
                        await ctx.channel.trigger_typing()
                        guessed = 'giveup'
                    elif player_guess == 'stop':
                        await ctx.channel.trigger_typing()
                        guessed = 'stop'
                    else:
                        await ctx.channel.trigger_typing()

                        guess_score = similar(movie['title'].lower(), player_guess)
                        if guess_score < 0.7: # Threshold for the guess.
                            wm_embed = discord.Embed(
                                title = what_movie_title,
                                description = f"{player_last_guessed} guessed __{player_guess}__ and was wrong! :x:\nMovie category: **{category}**",
                                color = discord.Colour.magenta()
                            )

                            if len(thesaurized_plot) > 1000:
                                for i in range(-(len(thesaurized_plot) // -1000)):
                                    if i == 0:
                                        wm_embed.add_field(
                                            name = '\u200b',
                                            value = f"__**Plot**__\n{thesaurized_plot[:(i+1)*1000]}...",
                                            inline = False
                                        )
                                    elif i-1 == -(len(thesaurized_plot) // -1000):
                                        wm_embed.add_field(
                                            name = '\u200b',
                                            value = f"...{thesaurized_plot[i*1000:]}",
                                            inline = False
                                        )
                                    else:
                                        wm_embed.add_field(
                                            name = '\u200b',
                                            value = f"...{thesaurized_plot[i*1000:(i+1)*1000]}...",
                                            inline = False
                                        )
                            else:
                                wm_embed.add_field(
                                        name = '\u200b',
                                        value = f"__**Plot**__\n{thesaurized_plot}",
                                        inline = False
                                    )
                            
                            wm_embed.add_field(
                                name = '\u200b',
                                value = what_movie_instructions,
                                inline = False
                            )

                            await wm_message.delete()
                            wm_message = await ctx.send(embed = wm_embed)

                        else:
                            guessed = 'yes'
                        
                    if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                        await player_message.delete()

                if guessed == 'giveup':
                    wm_embed = discord.Embed(
                        title = what_movie_title,
                        description = f"{player_last_guessed} gave up! :skull:\nThe movie was [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                        color = discord.Colour.red()
                    )
                    if movie['cover url'] is not None:
                        wm_embed.set_image(url = movie['cover url'])
                    await ctx.send(embed = wm_embed)
                    continue # Restart method via while loop.

                elif guessed == 'stop':
                    wm_embed = discord.Embed(
                        title = what_movie_title,
                        description = f"{player_last_guessed} ended the session! :no_entry_sign:\nGame Over.\nThe movie was [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                        color = discord.Colour.red()
                    )
                    if movie['cover url'] is not None:
                        wm_embed.set_image(url = movie['cover url'])
                    await ctx.send(embed = wm_embed)
                    ctx.command.reset_cooldown(ctx)
                    return

                elif guessed == 'yes':
                    wm_embed = discord.Embed(
                        title = what_movie_title,
                        description = f"{player_last_guessed} guessed __{player_guess}__ and {'was close enough' if guess_score < 0.9 else 'got it right'}! :tada:\nThe movie was [{movie['title']}](https://imdb.com/title/tt{movie_id})\nSend `wm new` to try again, or `wm stop` to immediately end the game session.",
                        color = discord.Colour.green()
                    )
                    wm_embed.set_thumbnail(url = player_message.author.display_avatar)
                    if movie['cover url'] is not None:
                        wm_embed.set_image(url = movie['cover url'])
                    await ctx.send(embed = wm_embed)

                    while True:
                        try:
                            player_message = await self.bot.wait_for('message', check = wm_check, timeout = wm_timeout)
                        except asyncio.TimeoutError:
                            ctx.command.reset_cooldown(ctx)
                            return
                        
                        if player_message.content.lower() == 'wm new':
                            if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                                await player_message.delete()
                            break

                        elif player_message.content.lower() == 'wm stop':
                            await ctx.channel.trigger_typing()
                            await ctx.send(f"{player_message.author.display_name} ended the session!")
                            if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                                await player_message.delete()
                            ctx.command.reset_cooldown(ctx)
                            return
                    
                    continue

                else:
                    log_message = f"Guessed variable is `{guessed}` which is not valid during a {ctx.command} invoked by {ctx.author} in {ctx.guild} - #{ctx.channel}."
                    logging.warning(log_message)
                    wm_embed = discord.Embed(
                        title = what_movie_title,
                        description = log_message
                    )
                    await ctx.send(embed = wm_embed)
                    ctx.command.reset_cooldown(ctx)
                    return
        
        elif mode == 'party':
            what_movie_instructions = f":warning: Remember to FORMAT your message with `wm <guess>` when attempting to guess! If everyone gives up, another movie will be selected. Send `wm giveup` to give up. The host {ctx.author.display_name} can also stop the session with `wm stop`."

            def get_scoreboard(participants, highest_point, giveup_list, win_board = False):
                sorted_players = sorted(participants.items(), key=lambda x: x[1]['point'], reverse=True)
                player_list = ""
                point_list = ""

                if win_board:
                    player_count = 1

                    if len(participants) < 3:
                        duo_match = True
                    else:
                        duo_match = False

                    for player in sorted_players:
                        if player_count == 1:
                            if duo_match:
                                player_list += ":crown:"
                            else:
                                player_list += ":first_place:"

                        elif player_count == 2:
                            player_2nd_points = player[1]['point']
                            if not duo_match:
                                player_list += ":second_place:"

                        elif player_count == 3:
                            if player[1]['point'] == player_2nd_points:
                                player_list += ":second_place:"
                            else:
                                player_list += ":third_place:"
                        
                        player_list += f"{player[1]['name']}\n"
                        point_list += f"{player[1]['point']}\n"
                        player_count += 1

                else:
                    for player in sorted_players:
                        if player[0] in giveup_list:
                            player_list += ":skull:"
                        if player[1]['point'] == highest_point:
                            player_list += ":crown:"
                        
                        player_list += f"{player[1]['name']}\n"
                        point_list += f"{player[1]['point']}\n"
                    
                return player_list, point_list
            
            def get_party_embed(what_movie_title, what_movie_instructions, round_num, guess_event, embed_color, win_point, player_list, point_list, thesaurized_plot):
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    color = embed_color
                ).add_field(
                    name = f"Round {round_num}",
                    value = f"{guess_event}Movie category: **{category}**\nFirst to **{win_point}** points wins!",
                    inline = False
                ).add_field(
                    name = "Player",
                    value = player_list,
                    inline = True
                ).add_field(
                    name = "Points",
                    value = point_list,
                    inline = True
                )

                if len(thesaurized_plot) > 1000:
                    for i in range(-(len(thesaurized_plot) // -1000)):
                        if i == 0:
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"__**Plot**__\n{thesaurized_plot[:(i+1)*1000]}...",
                                inline = False
                            )
                        elif i-1 == -(len(thesaurized_plot) // -1000):
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"...{thesaurized_plot[i*1000:]}",
                                inline = False
                            )
                        else:
                            wm_embed.add_field(
                                name = '\u200b',
                                value = f"...{thesaurized_plot[i*1000:(i+1)*1000]}...",
                                inline = False
                            )
                else:
                    wm_embed.add_field(
                            name = '\u200b',
                            value = f"__**Plot**__\n{thesaurized_plot}",
                            inline = False
                        )
                
                wm_embed.add_field(
                    name = '\u200b',
                    value = what_movie_instructions,
                    inline = False
                )

                return wm_embed                
            
            def get_result_embed(what_movie_title, round_num, guess_event, embed_color, movie_title, movie_id, movie_cover_url):
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    color = embed_color
                ).add_field(
                    name = f"Round {round_num}",
                    value = f"{guess_event}\nThe movie was [{movie_title}](https://imdb.com/title/tt{movie_id})",
                    inline = False
                )

                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie_cover_url)
                return wm_embed

            await ctx.respond(f"{ctx.author.display_name} is starting a game of WhatMovie! Category: {category}. Send `wm join` to join, then `wm start` to start the game. The host can send `wm stop` to end the session if you change your mind.")

            participants = {ctx.author.id: {'name': ctx.author.display_name, 'point': 0}}

            # Joining Session.
            while True:
                try:
                    user_message = await self.bot.wait_for('message', check = wm_check, timeout = wm_timeout)
                except asyncio.TimeoutError:
                    ctx.command.reset_cooldown(ctx)
                    return

                if user_message.content.lower() == 'wm join':
                    if user_message.author.id not in participants:
                        await ctx.channel.trigger_typing()
                        participants[user_message.author.id] = {'name': user_message.author.display_name, 'point': 0}
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await user_message.delete()
                        await ctx.send(f"{user_message.author.display_name} has joined.")
                    else:
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await user_message.delete()
                        await ctx.send(f"{user_message.author.display_name} has already joined!")
                    continue

                elif user_message.content.lower() == 'wm start':
                    await ctx.channel.trigger_typing()

                    if len(participants) < 2:
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await user_message.delete()
                        await ctx.send(f"You can't play party mode all by yourself! If you're a loner send `wm stop` and go play freeplay mode with `/wm mode:freeplay`.")
                        continue

                    elif user_message.author.id in participants:
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await user_message.delete()
                        break
                
                elif user_message.content.lower() == 'wm stop':
                    if user_message.author.id == ctx.author.id:
                        await ctx.channel.trigger_typing()
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await user_message.delete()
                        await ctx.send("Session ended!")
                        ctx.command.reset_cooldown(ctx)
                        return
            
            # Initialise start game values.
            round_num = 1
            win_point = win if win != 'default' else len(participants)*2

            # Start of party session.
            while True:
                await ctx.respond("Hmmm which movie shall I choose? :thinking: Lemme see...")
                await ctx.channel.trigger_typing()

                movie, movie_id, thesaurized_plot = get_movie(category)
                movie_title = movie['title']
                movie_cover_url = movie['cover url']

                points = [participants[player]['point'] for player in participants]
                if len(set(points)) != 1:
                    highest_point = max(points)
                else:
                    highest_point = None

                giveup_list = []
                player_list, point_list = get_scoreboard(participants, highest_point, giveup_list)

                if isinstance(highest_point, int):
                    if win_point - highest_point == 1:
                        what_movie_title = ":trophy: What movie is this? Match Point! :trophy:"

                guess_event = ""
                embed_color = discord.Colour.magenta()
                wm_embed = get_party_embed(what_movie_title, what_movie_instructions, round_num, guess_event, embed_color, win_point, player_list, point_list, thesaurized_plot)
                wm_message = await ctx.send(embed = wm_embed)
                player_guessed_right = None

                # While guessing the movie.
                while True:
                    try:
                        player_message = await self.bot.wait_for('message', check = wm_check, timeout = wm_timeout)
                    except asyncio.TimeoutError:
                        logging.info(f"No one responded for too long during {ctx.command} invoked by {ctx.author} in {ctx.guild} - #{ctx.channel}")
                        wm_embed = discord.Embed(
                            title = what_movie_title,
                            description = f"No one responded for too long. :shrug:\nGame over.\nThe movie was [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                            color = discord.Colour.red()
                        )
                        if movie['cover url'] is not None:
                            wm_embed.set_image(url = movie['cover url'])
                        await ctx.send(embed = wm_embed)
                        ctx.command.reset_cooldown(ctx)
                        return
                    
                    if player_message.content == 'wm stop':
                        if player_message.author.id == ctx.author.id:
                            await ctx.channel.trigger_typing()
                            guess_event = f"The host {ctx.author.display_name} stopped the session! :no_entry_sign:\nGame Over.\n"
                            embed_color = discord.Colour.red()
                            wm_embed = get_result_embed(what_movie_title, round_num, guess_event, embed_color, movie_title, movie_id, movie_cover_url)
                            
                            if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                                await player_message.delete()
                            await ctx.send(embed = wm_embed)
                            ctx.command.reset_cooldown(ctx)
                            return

                    if player_message.author.id in participants and player_message.author.id not in giveup_list:
                        player_last_guessed = player_message.author.display_name
                        player_guess = player_message.content[3:].lower()

                        if player_guess == 'giveup':
                            await ctx.channel.trigger_typing()
                            
                            giveup_list.append(player_message.author.id)

                            if len(giveup_list) == len(participants):
                                guess_event = f"{player_last_guessed} gave up as well! It seems everyone gave this one up! :skull:\n"
                                embed_color = discord.Colour.red()
                                wm_embed = get_result_embed(what_movie_title, round_num, guess_event, embed_color, movie_title, movie_id, movie_cover_url)
                                break

                            else:
                                guess_event = f"{player_last_guessed} gave up! :skull:\n"
                                embed_color = discord.Colour.gold()
                                player_list, point_list = get_scoreboard(participants, highest_point, giveup_list)
                                
                                wm_embed = get_party_embed(what_movie_title, what_movie_instructions, round_num, guess_event, embed_color, win_point, player_list, point_list, thesaurized_plot)

                        else:
                            await ctx.channel.trigger_typing()
                            guess_score = similar(movie['title'].lower(), player_guess)

                            if guess_score < 0.7: # Threshold for the guess.
                                guess_event = f"{player_last_guessed} guessed __{player_guess}__ and was wrong! :x:\n"
                                embed_color = discord.Colour.magenta()
                                wm_embed = get_party_embed(what_movie_title, what_movie_instructions, round_num, guess_event, embed_color, win_point, player_list, point_list, thesaurized_plot)

                            else:
                                guess_event = f"{player_last_guessed} guessed __{player_guess}__ and {'was close enough' if guess_score < 0.9 else 'got it right'}! :tada:\n"
                                embed_color = discord.Colour.green()

                                participants[player_message.author.id]['point'] += 1
                                player_guessed_right = player_message.author.id
                                player_guessed_right_avatar = player_message.author.display_avatar

                                wm_embed = get_result_embed(what_movie_title, round_num, guess_event, embed_color, movie_title, movie_id, movie_cover_url)
                                wm_embed.set_thumbnail(url = player_guessed_right_avatar)
                                break
                            
                        if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                            await player_message.delete()
                        await wm_message.delete()
                        wm_message = await ctx.send(embed = wm_embed)
                
                # End of round.
                if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                    await player_message.delete()
                await wm_message.delete()
                wm_message = await ctx.send(embed = wm_embed)

                if player_guessed_right != None:
                    if participants[player_guessed_right]['point'] >= win_point:
                        winner = participants[player_guessed_right]
                        break

                round_num += 1
            
            # End of party session due to winner.
            player_list, point_list = get_scoreboard(participants, winner['point'], [], True)
            win_embed = discord.Embed(
                title = ":tada: What movie is this? Game won! :tada:",
                color = embed_color
            ).add_field(
                name = f"Round {round_num}",
                value = f"Movie category: **{category}**\n:trophy: **{winner['name']}** won the game with **{winner['point']}** points! :trophy:",
                inline = False
            ).add_field(
                name = "Player",
                value = player_list,
                inline = True
            ).add_field(
                name = "Points",
                value = point_list,
                inline = True
            ).set_thumbnail(url = player_guessed_right_avatar)
            await ctx.send(embed = win_embed)
            ctx.command.reset_cooldown(ctx)

    @what_movie.error
    async def what_movie_handler(self, ctx, error):
        ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.CommandOnCooldown):
            logging.info(f"{ctx.author} tried to run {ctx.command} in {ctx.guild} - #{ctx.channel} while an instance is already running.")
            await ctx.respond(f"A game of {ctx.command} is already running on this channel!")

        elif isinstance(error, IMDbError):
            log_message = f"IMDbError invoked by: {ctx.author}. During {ctx.command}. Server and channel: {ctx.guild} - #{ctx.channel}. Ignoring exception in command {ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            logging.warning(log_message)
            print("[ERROR] " + log_message)

        else:
            log_message = f"Invoked by: {ctx.author}. During {ctx.command}. Server and channel: {ctx.guild} - #{ctx.channel}. Ignoring exception in command {ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            logging.warning(log_message)
            print("[ERROR] " + log_message)
            await ctx.send("An error has occurred! Check the logs for details.")

def setup(bot):
    bot.add_cog(Games(bot))
