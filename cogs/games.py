import discord
from discord.ext import commands
import sys

import pytz
from datetime import datetime, timezone
import random
import asyncio
import traceback

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from difflib import SequenceMatcher

from toolbox import moviez
import imdb
ia = imdb.IMDb()
top = ia.get_top250_movies()

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'rps',
        description = "Rock, Paper, Scissors!"
    )
    @commands.guild_only()
    async def rps_command(self, ctx, choice = 'none'):
        await ctx.channel.trigger_typing()

        if choice == 'none':
            await ctx.send(content = f"To use this command, type `{ctx.prefix}{ctx.invoked_with} <choice>`\nChoices: `r/rock, p/paper, s/scissors`")
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
                await ctx.send(content = f"Wrong command bro, what the heck is {choice}?")
                return
            elif choice.lower() in option_aliases:
                player = (ctx.message.author.display_name, options[option_aliases.index(choice.lower())])
            else:
                player = (ctx.message.author.display_name, choice.lower())
            
            cpu = (ctx.guild.me.display_name, options[random.randrange(len(options))])
            
            rps_embed = discord.Embed(
                title = 'Rock, Paper, Scissors!',
                description = f"{ctx.message.author.display_name} used {option_emoji[options.index(player[1])]}!\n{ctx.guild.me.display_name} used {option_emoji[options.index(cpu[1])]}!\n\n"
            )

            if rps_sesh(player, cpu) == 'draw':
                rps_embed.description += "It's a Draw!"
                rps_embed.color = 0xF1C40F # GOLD
            elif rps_sesh(player, cpu) == ctx.guild.me.display_name:
                rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
                rps_embed.color = 0xE74C3C # RED
                rps_embed.set_thumbnail(url = self.bot.user.avatar_url)
            else:
                rps_embed.description += f"{rps_sesh(player, cpu)} wins! :tada:"
                rps_embed.color = 0x2ECC71 # GREEN
                rps_embed.set_thumbnail(url = ctx.message.author.avatar_url)

            await ctx.send(embed = rps_embed)

    @commands.command(
        name = 'charge',
        description = '''Challenge me to a battle of wits and resources until one of us loses!
The main feature of this game is mana. Moves you can perform will have different mana costs.
During a match, type `c<space>moves` to see the movelist. Start a move with the message `c<space>`.'''
    )
    @commands.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    async def charge_command(self, ctx):
        await ctx.channel.trigger_typing()
        move_dict = {
                'charge': {'cost': -1, 'status': 'restore', 'stylized': ':zap:Charge'},
                'block': {'cost': 0, 'status': 'defence', 'stylized': ':shield:Block'},
                'jump': {'cost': 0, 'status': 'defence', 'stylized': ':runner:Jump'},
                'bom': {'cost': 1, 'status': 'attack', 'stylized': ':comet:Bom'},
                'boom': {'cost': 2, 'status': 'attack', 'stylized': ':boom:Boom'},
                'slash': {'cost': 2, 'status': 'attack', 'stylized': ':crossed_swords:Slash'},
                'fwoosh': {'cost': 4, 'status': 'attack', 'stylized': ':wind_blowing_face:Fwoosh'},
                'stop': {'cost': 0, 'status': 'dead', 'stylized': ':flag_white: Gave up'}
        }

        def print_error(error_message):
            log_message = f"[ERROR] {error_message}\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)

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
                move = 'fwoosh'
            elif player.mana == 0:
                move = random.choice(list(move_dict))
                while move == 'stop' or cpu.mana - move_dict[move]['cost'] < 0 or move_dict[move]['status'] == 'defence':
                    move = random.choice(list(move_dict))
            else:
                if random.randrange(100) < 20:
                    move = 'charge'
                else:
                    move = random.choice(list(move_dict))
                    while move == 'stop' or cpu.mana - move_dict[move]['cost'] < 0:
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
                print_error(f"No such situation called {situation}!")
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
                print_error("Code should not reach here!")
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
                print_error("Code should not reach here!")
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
                print_error("Code should not reach here!")
                return "[ERROR] Code should not reach here!"
            loser.die()
            return announce('attack_overpower', winner, loser)

        # Define a check function that validates the message received by the bot
        def check(m):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return m.channel == ctx.message.channel and m.author == ctx.message.author
        
        player = Player(ctx.message.author.display_name)
        player_avatar = ctx.message.author.avatar_url
        cpu = Player(ctx.guild.me.display_name)
        cpu_avatar = self.bot.user.avatar_url
        
        # Initialise embed
        charge_embed = discord.Embed(
            title = 'Charge',
            description = f"{player.name} challenged {cpu.name} to a game of Charge!\n{player.name} used {player.move}!\n{cpu.name} used {cpu.move}!",
            color = 0x3498DB # BLUE
        )
        
        # Game until one player loses
        while player.status != 'dead' and cpu.status != 'dead':
            charge_embed.add_field(
                name = '\u200b',
                value = f"+-------------------------------+\n{player.name}'s :yin_yang:Mana: {player.mana}\n+-------------------------------+\n{cpu.name}'s :yin_yang:Mana: {cpu.mana}\n+-------------------------------+\n\n:warning:Remember to start every move with `c<space>`!\nNext move?",
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
                msg = await self.bot.wait_for('message', check = check, timeout = 30)
                if msg.content[:2].lower() == 'c ':
                    await ctx.channel.trigger_typing()
                    player_move = msg.content[2:].lower()
                    valid = 'yes'
            if player_move == 'moves':
                await ctx.send(content = '''`+--------+------+-------------------+
| Move   | Cost | Description       |
+--------+------+-------------------+
| Charge | None | +1 Mana           |
+--------+------+-------------------+
| Block  | None | Blocks Bom, Slash |
+--------+------+-------------------+
| Jump   | None | Dodges Bom, Boom  |
+--------+------+-------------------+
| Bom    | 1    | Level 1 Attack    |
+--------+------+-------------------+
| Boom   | 2    | Level 2 Attack    |
+--------+------+-------------------+
| Slash  | 2    | Level 2 Attack    |
+--------+------+-------------------+
| Fwoosh | 4    | Level 4 Attack    |
+--------+------+-------------------+
| Stop   | None | Give up!          |
+--------+------+-------------------+`''')
                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = "Aight there's yer movelist.",
                    color = 0x3498DB # BLUE
                )
                continue
            elif player_move not in move_dict:
                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = f"What kind of move is {player_move}?!\nType `c<space>moves` to see the movelist.",
                    color = 0x3498DB
                )
                continue
            elif player.mana - move_dict[player_move]['cost'] < 0:
                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = "Not enough mana!",
                    color = 0x3498DB
                )
                continue
            else:
                player.use_move(player_move, move_dict[player_move]['cost'])
                cpu.use_move(cpu_move, move_dict[cpu_move]['cost'])

            charge_embed = discord.Embed(
                title = 'Charge!',
                description = f"{player.name}: {player.move}\n{cpu.name}: {cpu.move}",
                color = 0x3498DB # BLUE
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
            print_error("Something wrong occurred during the fight. Both dead.")
            await ctx.send(content = "[ERROR] Something wrong occurred during the fight. Both dead.")
        elif player.status == 'dead':
            charge_embed.add_field(
                name = '\u200b',
                value = f"{cpu.name} WINS! :tada:",
                inline = False
            )
            charge_embed.color = 0xE74C3C # RED
            charge_embed.set_thumbnail(url = self.bot.user.avatar_url)
            await ctx.send(embed = charge_embed)
        elif cpu.status == 'dead':
            charge_embed.add_field(
                name = '\u200b',
                value = f"{player.name} WINS! :tada:",
                inline = False
            )
            charge_embed.color = 0x2ECC71 # GREEN
            charge_embed.set_thumbnail(url = ctx.message.author.avatar_url)
            await ctx.send(embed = charge_embed)
        else:
            print_error("Both players are still alive. Code should not have reached here.")
            await ctx.send(content = "[ERROR] Both players are still alive. Code should not have reached here.")
        
        ctx.command.reset_cooldown(ctx)
    
    @charge_command.error
    async def charge_command_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            log_message = f"[INFO] {ctx.message.author} tried to run Charge in {ctx.guild} - #{ctx.channel} while an instance is already running.\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)
            await ctx.send(content = f"A game of Charge is already running on this channel!")
        elif isinstance(error, commands.CommandInvokeError):
            log_message = f"[INFO] {ctx.message.author} took to long to respond during Charge in {ctx.guild} - #{ctx.channel}\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)
            charge_embed = discord.Embed(
                title = 'Charge!',
                description = f"{ctx.message.author.display_name}, you took too long to respond!\n{ctx.guild.me.display_name} WINS! :tada:"
            )
            charge_embed.color = 0xE74C3C # RED
            charge_embed.set_thumbnail(url = self.bot.user.avatar_url)
            await ctx.send(embed = charge_embed)
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(content = f"Whoa {ctx.message.author.name}?! Sorry, but if you wanna fight me, do it in a server. I'd rather beat you when everyone is looking :sunglasses:")
        else:
            log_message = f"[ERROR] Invoked by: {ctx.message.author}\nServer and channel: {ctx.guild} - #{ctx.channel}\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}\nIgnoring exception in command {ctx.prefix}{ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)

    @commands.command(
        name = 'whatmovie',
        description = "Guess a random movie given a thesaurized plot!\nYou have 5 chances!\nYou may also choose a category by adding the category name after the command.\nCategories:\n`top` - (default) top 250 movies\n`marvel`\n\nDuring a game, start your messages with `wm<space>` when guessing.\n\nMovie data source is provided by the folks who made the IMDbPY package! :grin:\nVisit them at https://imdbpy.github.io/",
        aliases = ['wm']
    )
    @commands.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    async def tsr_movie_command(self, ctx, category = 'top'):
        while True:
            await ctx.channel.trigger_typing()

            def similar(a, b):
                return SequenceMatcher(None, a, b).ratio()

            def check(m):
                # Look for the message sent in the same channel where the command was used
                # As well as by the user who used the command.
                return m.channel == ctx.message.channel

            def thesaurize(input_string):
                skip_words = ['who']
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

            load_message = await ctx.send(content = "Hmmm which movie shall I choose? :thinking: Lemme see...")
            await ctx.channel.trigger_typing()

            category = category.lower()
            if category not in moviez:
                await ctx.send(content = f"We don't have `{category}`.\nCategory list:\n`top` - (default) top 250 movies\n`marvel`")
                ctx.command.reset_cooldown(ctx)
                break
            elif category == 'top':
                random_movie = top[random.randrange(0,len(top)+1)]
                movie_id = random_movie.movieID
                movie = ia.get_movie(movie_id)
            else:
                full_movie_id = random.choice(moviez[category]['id'])
                movie_id = full_movie_id[2:]
                movie = ia.get_movie(movie_id)

            movie_plot = movie['plot'][random.randrange(0, len(movie['plot']))]

            # Prevent error where embed.description hits over 2048 characters
            while len(movie_plot) > 2000:
                movie_plot = movie['plot'][random.randrange(0, len(movie['plot']))]
            thesaurized_plot = thesaurize(movie_plot)

            lives = moviez[category]['lives']
            lives_string = 'lives'
            wm_embed = discord.Embed(
                title = 'What movie is this?',
                description = f"You have **{lives}** {lives_string}\nCategory: {category}\n\n__**Plot**__\n{thesaurized_plot}",
                color = 0x7289DA # BLURPLE
            ).add_field(
                name = '\u200b',
                value = ":warning: Remember to START your message with `wm<space>` when attempting to guess! Send `skip` to get a different movie, or `stop` to give up.",
                inline = False
            )
            wm_message = await ctx.send(embed = wm_embed)
            await load_message.delete()
            guessed = 'no'

            while guessed == 'no':
                player_message = await self.bot.wait_for('message', check = check, timeout = 120)
                if player_message.content.lower() == 'skip':
                    guessed = 'skip'
                elif player_message.content.lower() == 'stop':
                    guessed = 'stop'
                elif player_message.content[:3].lower() == 'wm ':
                    await ctx.channel.trigger_typing()
                    if similar(movie['title'].lower(), player_message.content[3:].lower()) < 0.7:
                        lives -= 1
                        if lives == 1:
                            lives_string = 'life'
                        elif lives == 0:
                            break
                        await wm_message.delete()
                        wm_embed = discord.Embed(
                            title = 'What movie is this?',
                            description = f":x:\n{player_message.author.display_name} was wrong!\nYou have **{lives}** {lives_string} left!\nCategory: {category}\n\n__**Plot**__\n{thesaurized_plot}",
                            color = 0x7289DA # BLURPLE
                        ).add_field(
                            name = '\u200b',
                            value = ":warning: Remember to START your message with `wm<space>` when attempting to guess! Send `skip` to get a different movie, or `stop` to give up.",
                            inline = False
                        )
                        wm_message = await ctx.send(embed = wm_embed)
                    else:
                        guessed = 'yes'

            if guessed == 'skip':
                wm_embed = discord.Embed(
                    title = 'What movie is this?',
                    description = f":no_entry_sign:\nSkipped! Game Over.\nThe movie is: {movie['title']}\nhttps://imdb.com/title/tt{movie_id}",
                    color = 0xE74C3C # RED
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])
                await ctx.send(embed = wm_embed)
                continue # Restart method
            elif guessed == 'stop':
                wm_embed = discord.Embed(
                    title = 'What movie is this?',
                    description = f":no_entry_sign:\nGave up! Game Over.\nThe movie is: {movie['title']}\nhttps://imdb.com/title/tt{movie_id}",
                    color = 0xE74C3C # RED
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])
            elif lives == 0:
                wm_embed = discord.Embed(
                    title = 'What movie is this?',
                    description = f":broken_heart:\nNo more lives! Game Over.\nThe movie is: {movie['title']}\nhttps://imdb.com/title/tt{movie_id}",
                    color = 0xE74C3C # RED
                )
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])
            elif guessed == 'yes':
                wm_embed = discord.Embed(
                    title = 'What movie is this?',
                    description = f"{player_message.author.display_name} got it right! :tada:\nThe movie is: {movie['title']}\nhttps://imdb.com/title/tt{movie_id}",
                    color = 0x2ECC71 # GREEN
                )
                wm_embed.set_thumbnail(url = player_message.author.avatar_url)
                if movie['cover url'] is not None:
                    wm_embed.set_image(url = movie['cover url'])
            else:
                log_message = f"[ERROR] No one guessed right and lives were still above 0 during a WhatMovie in {ctx.guild} - #{ctx.channel}.\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
                with open("./logs/weeblord.log", "a+") as f:
                    f.write(f"\n{log_message}")
                print(log_message)
                wm_embed = discord.Embed(
                    title = 'What movie is this?',
                    description = log_message
                )

            await ctx.send(embed = wm_embed)
            ctx.command.reset_cooldown(ctx)
            return

    @tsr_movie_command.error
    async def tsr_movie_command_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            log_message = f"[INFO] {ctx.message.author} tried to run WhatMovie in {ctx.guild} - #{ctx.channel} while an instance is already running.\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)
            await ctx.send(content = f"A game of WhatMovie is already running on this channel!")
        elif isinstance(error, commands.CommandInvokeError):
            log_message = f"[INFO] No one responded for too long during WhatMovie in {ctx.guild} - #{ctx.channel}\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}\n{error}")
            print(f"{log_message}\n{error}")
            wm_embed = discord.Embed(
                title = 'What movie is this?',
                description = f"No one responded. :shrug:\nGame over.",
                color = 0xE74C3C # RED
            )
            await ctx.send(embed = wm_embed)
            ctx.command.reset_cooldown(ctx)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(content = f"This game is wayy more fun when played in a server, so I ain't just playin with you {ctx.message.author.name}.")
        else:
            log_message = f"[ERROR] Invoked by: {ctx.message.author}\nServer and channel: {ctx.guild} - #{ctx.channel}\nTimestamp: {datetime.now(timezone.utc).astimezone(pytz.timezone('Singapore'))}\nIgnoring exception in command {ctx.prefix}{ctx.command}: {traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)}"
            with open("./logs/weeblord.log", "a+") as f:
                f.write(f"\n{log_message}")
            print(log_message)


def setup(bot):
    bot.add_cog(Games(bot))
