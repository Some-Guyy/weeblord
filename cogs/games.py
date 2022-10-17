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

class Games(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = 'rps', description = "Rock, paper, scissors!")
    @discord.option('move', choices = ['rock', 'paper', 'scissors'])
    async def rps(self, ctx, move: str):
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
        
        move_list = ['rock', 'paper', 'scissors']
        move_emoji = [':new_moon:', ':newspaper:', ':scissors:'] # For discord emoji
        player = (ctx.author.display_name, move)
        cpu = (self.bot.user.display_name, move_list[random.randrange(len(move_list))])
        
        rps_embed = discord.Embed(
            title = 'Rock, Paper, Scissors!',
            description = f"{ctx.author.display_name} used {move_emoji[move_list.index(player[1])]}!\n{self.bot.user.display_name} used {move_emoji[move_list.index(cpu[1])]}!\n\n"
        )

        if rps_sesh(player, cpu) == 'draw':
            rps_embed.description += "It's a Draw!"
            rps_embed.color = discord.Colour.gold()

        elif rps_sesh(player, cpu) == self.bot.user.display_name:
            rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
            rps_embed.color = discord.Colour.red()
            rps_embed.set_thumbnail(url = self.bot.user.display_avatar)

        else:
            rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
            rps_embed.color = discord.Colour.green()
            rps_embed.set_thumbnail(url = ctx.author.display_avatar)

        await ctx.respond(embed = rps_embed)

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
                description = "Challenge me to a battle of wits and resources until one of us loses!\nThe main feature of this game is mana. Moves you can perform will have different mana costs. During a match, use `c <move>` to use a move.",
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
            def check(message: discord.Message):
                # Look for the message sent in the same channel where the command was used
                # As well as by the user who used the command.
                return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id

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
                        move_message = await self.bot.wait_for('message', check = check, timeout = 30)
                    except asyncio.TimeoutError:
                        logging.info(f"{ctx.author} took to long to respond during Charge in {ctx.guild} - #{ctx.channel}")
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
        if isinstance(error, commands.CommandOnCooldown):
            logging.info(f"{ctx.author} tried to run {ctx.command} in {ctx.guild} - #{ctx.channel} while an instance is already running.")
            await ctx.respond(f"A game of {ctx.command} is already running on this channel!")

        else:
            log_message = f"Invoked by: {ctx.author}. During {ctx.command}. Server and channel: {ctx.guild} - #{ctx.channel}. Ignoring exception in command {ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            logging.warning(log_message)
            print("[ERROR] " + log_message)

    @discord.slash_command(name = 'whatmovie', description = "Guess a random movie given a thesaurized plot!")
    @discord.option('category', description = "Category of movies.", choices = ['top', 'popular', 'shitty', 'marvel'], default = 'top')
    @discord.option('lives', description = "Number of chances you can get it wrong.", min_value = 1, max_value = 10, default = 'unlimited')
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    async def what_movie(self, ctx, category: str, lives: int):
        what_movie_title = "What movie is this?"
        what_movie_instructions = ":warning: Remember to FORMAT your message with `wm <guess>` when attempting to guess! Send `wm skipwm` to get a different movie, or `wm giveup` to give up."

        while True:
            await ctx.channel.trigger_typing()
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

            def check(message: discord.Message):
                # Look for the message sent in the same channel where the command was used
                return message.channel.id == ctx.channel.id

            await ctx.respond("Hmmm which movie shall I choose? :thinking: Lemme see...")
            await ctx.channel.trigger_typing()

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

            # Prevent error where embed.description hits over 2048 characters
            long_plot = True
            while long_plot:
                movie_plot = movie['plot'][random.randrange(0, len(movie['plot']))]
                thesaurized_plot = thesaurize_string(movie_plot)
                if len(thesaurized_plot) <= 2048:
                    long_plot = False

            if lives == 1:
                lives_string = 'life'
            else:
                lives_string = 'lives'

            wm_embed = discord.Embed(
                title = what_movie_title,
                description = f"You have **{lives}** {lives_string}\nCategory: {category}\n\n__**Plot**__\n{thesaurized_plot}",
                color = discord.Colour.magenta()
            ).add_field(
                name = '\u200b',
                value = what_movie_instructions,
                inline = False
            )

            wm_message = await ctx.send(embed = wm_embed)
            guessed = 'no'

            while guessed == 'no':
                try:
                    player_message = await self.bot.wait_for('message', check = check, timeout = 120)
                except asyncio.TimeoutError:
                    logging.info(f"No one responded for too long during {ctx.command} invoked by {ctx.author} in {ctx.guild} - #{ctx.channel}")
                    wm_embed = discord.Embed(
                        title = what_movie_title,
                        description = f"No one responded. :shrug:\nGame over.",
                        color = discord.Colour.red()
                    )
                    await ctx.send(embed = wm_embed)
                    ctx.command.reset_cooldown(ctx)
                    return

                if player_message.content[:3].lower() == 'wm ':
                    player_guess = player_message.content[3:].lower()

                    if player_guess == 'skipwm':
                        guessed = 'skip'
                    elif player_guess == 'giveup':
                        guessed = 'giveup'
                    else:
                        await ctx.channel.trigger_typing()

                        if similar(movie['title'].lower(), player_guess) < 0.7: # Threshold for the guess.
                            if isinstance(lives, int):
                                lives -= 1

                                if lives == 1:
                                    lives_string = 'life'
                                elif lives == 0:
                                    break

                            wm_embed = discord.Embed(
                                title = what_movie_title,
                                description = f":x:\n{player_message.author.display_name} guessed *{player_guess}* and was wrong!\nYou have **{lives}** {lives_string} left!\nCategory: {category}\n\n__**Plot**__\n{thesaurized_plot}",
                                color = discord.Colour.magenta()
                            ).add_field(
                                name = '\u200b',
                                value = what_movie_instructions,
                                inline = False
                            )

                            if ctx.channel.type is discord.ChannelType.text: # Delete only if its in a server channel.
                                await player_message.delete()
                            await wm_message.delete()
                            wm_message = await ctx.send(embed = wm_embed)

                        else:
                            guessed = 'yes'

            if guessed == 'skip':
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = f":no_entry_sign:\nSkipped! Game Over.\nThe movie is [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                    color = discord.Colour.red()
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])
                await ctx.send(embed = wm_embed)
                continue # Restart method via while loop.

            elif guessed == 'giveup':
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = f":no_entry_sign:\nGave up! Game Over.\nThe movie is [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                    color = discord.Colour.red()
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])

            elif lives == 0:
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = f":broken_heart:\nNo more lives! Game Over.\nThe movie is [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                    color = discord.Colour.red()
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])

            elif guessed == 'yes':
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = f"{player_message.author.display_name} got it right! :tada:\nThe movie is [{movie['title']}](https://imdb.com/title/tt{movie_id})",
                    color = discord.Colour.green()
                )
                wm_embed.set_thumbnail(url = player_message.author.display_avatar)
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])

            else:
                log_message = f"No one guessed right and lives were still above 0 during a {ctx.command} invoked by {ctx.author} in {ctx.guild} - #{ctx.channel}."
                logging.warning(log_message)
                wm_embed = discord.Embed(
                    title = what_movie_title,
                    description = log_message
                )

            await ctx.send(embed = wm_embed)
            ctx.command.reset_cooldown(ctx)
            return # To break out of the while loop.

    @what_movie.error
    async def what_movie_handler(self, ctx, error):
        what_movie_title = 'What movie is this?'

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

def setup(bot):
    bot.add_cog(Games(bot))
