import discord
from discord.ext import commands

import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            string += " UwU"
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
        name = 'charge',
        description = '''A battle of wits and resources until one loses!
The main feature of this game is mana. Moves you can perform will have different mana costs.
Type `$charge moves` for movelist'''
    )
    async def charge_command(self, ctx, info = 'none'):
        class Player:
            def __init__(self, name):
                self.name = name
                self.mana = 1
                self.status = 'standby'
            
            def use_move(self, move_name, cost):
                self.move = move_name
                self.mana -= cost
                self.power = cost
                if self.move == 'charge':
                    self.status = 'restore'
                elif cost == 0:
                    self.status = 'defence'
                    self.power = 2
                else:
                    self.status = 'attack'
            
            def die(self):
                self.status = 'dead'
            
        def announce(situation, winner, loser):
            # During non-winner/loser cases they will still be used in place of player1/player2 or charger/defender
            lines = {
                'both_restore': [
                    f"Both used {winner.move}! The tension between them continues to rise...",
                    f"Both used {winner.move}! The tension betweeen them rises...",
                    f"Both used {winner.move}! The air thickens.",
                    f"Both used {winner.move}! An aura of power can be felt throughout the air.."
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
                    f"Both used {winner.move}! The powers cancelled each other out!",
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
                ]
            }
            if situation in lines:
                return discord.Embed(title = 'Charge!', description = random.choice(lines[situation]), color = 0x3498DB)
            else:
                print(f"[ERROR] No such situation called {situation}!")
        
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
                print("[ERROR] Code should not reach here!")
                player1.die()
                player2.die()
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
                if attacker.move == 'boom' and defender.move == 'jump' or attacker.move == 'slash' and defender.move == 'block':
                    return announce('defend_overpower', defender, attacker)
                else:
                    defender.die()
                    return announce('attack_overpower', attacker, defender)
            elif attacker.power < defender.power:
                return announce('defend_overpower', defender, attacker)
            else:
                print("[ERROR] Code should not reach here!")
                player1.die()
                player2.die()
                
        def attack_overpower(player1, player2):
            if player1.power > player2.power:
                winner = player1
                loser = player2
            elif player1.power < player2.power:
                winner = player2
                loser = player1
            else:
                print("[ERROR] Code should not reach here!")
                player1.die()
                player2.die()
                return
            loser.die()
            return announce('attack_overpower', winner, loser)

        # Define a check function that validates the message received by the bot
        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author
        
        if info == 'moves':
            await ctx.send(content = '''```+--------+------+-----------------------------------------------------------------+
| Move   | Cost | Description                                                     |
+--------+------+-----------------------------------------------------------------+
| Charge | None | Increases your mana by 1. Vulnerable to ANY attack.             |
+--------+------+-----------------------------------------------------------------+
| Block  | None | Blocks “Bom” and “Slash”. Vulnerable to any OTHER attack.       |
+--------+------+-----------------------------------------------------------------+
| Jump   | None | Jumps above “Bom” and “Boom”. Vulnerable to any OTHER attack.   |
+--------+------+-----------------------------------------------------------------+
| Bom    | 1    | Shoots a small energy ball, loses to any other stronger attack. |
+--------+------+-----------------------------------------------------------------+
| Boom   | 2    | Shoots a huge energy ball, loses to “Smash”                     |
+--------+------+-----------------------------------------------------------------+
| Slash  | 2    | Slashes wildly, loses to “Smash”                                |
+--------+------+-----------------------------------------------------------------+
| Smash  | 4    | Smashes the opponent with enormous power.                       |
+--------+------+-----------------------------------------------------------------+```''')
            return
        elif info != 'none':
            await ctx.send(content = f"Type `{ctx.prefix}charge` to challenge me to a game of Charge! Or `{ctx.prefix}charge moves` to view the movelist.")
            return
        else:    
            player = Player(ctx.message.author.name)
            player_avatar = ctx.message.author.avatar_url
            cpu = Player(self.bot.user.name)
            cpu_avatar = self.bot.user.avatar_url
            move_dict = {
                'charge': {'cost': -1, 'defeat': 'none'},
                'block': {'cost': 0, 'defeat': 'none'},
                'jump': {'cost': 0, 'defeat': 'none'},
                'bom': {'cost': 1, 'defeat': ['charge']},
                'boom': {'cost': 2, 'defeat': ['charge', 'block', 'bom']},
                'slash': {'cost': 2, 'defeat': ['charge', 'jump', 'bom']},
                'smash': {'cost': 4, 'defeat': ['charge', 'block', 'jump', 'bom', 'boom', 'slash']}
            }
            
            charge_embed = discord.Embed(
                title = 'Charge',
                description = f"{player.name} challenged {cpu.name} to a game of Charge!\n{player.name} charged!\n{cpu.name} charged!\n\nNext move?",
                color = 0x3498DB # BLUE
            )
            
            # Game until one player loses
            while player.status != 'dead' and cpu.status != 'dead':
                charge_embed.add_field(
                    name = '\u200b',
                    value = f"+-------------------------------+\n{player.name}'s mana: {player.mana}\n+-------------------------------+\n{cpu.name}'s mana: {cpu.mana}\n+-------------------------------+\n\nNext move?",
                    inline = False
                )
                await ctx.send(embed = charge_embed)

                # Player move
                msg = await self.bot.wait_for('message', check = check)
                player_move = msg.content
                if player_move == 'moves':
                    await ctx.send(content = '''`+--------+------+-----------------------------------------------------------------+
| Move   | Cost | Description                                                     |
+--------+------+-----------------------------------------------------------------+
| Charge | None | Increases your mana by 1. Vulnerable to ANY attack.             |
+--------+------+-----------------------------------------------------------------+
| Block  | None | Blocks “Bom” and “Slash”. Vulnerable to any OTHER attack.       |
+--------+------+-----------------------------------------------------------------+
| Jump   | None | Jumps above “Bom” and “Boom”. Vulnerable to any OTHER attack.   |
+--------+------+-----------------------------------------------------------------+
| Bom    | 1    | Shoots a small energy ball, loses to any other stronger attack. |
+--------+------+-----------------------------------------------------------------+
| Boom   | 2    | Shoots a huge energy ball, loses to “Smash”                     |
+--------+------+-----------------------------------------------------------------+
| Slash  | 2    | Slashes wildly, loses to “Smash”                                |
+--------+------+-----------------------------------------------------------------+
| Smash  | 4    | Smashes the opponent with enormous power.                       |
+--------+------+-----------------------------------------------------------------+`''')
                    continue
                elif player_move not in move_dict:
                    charge_embed = discord.Embed(
                        title = 'Charge!',
                        description = f"What kind of move is {player_move}?!\nType `moves` to see the movelist.",
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
                    
                # CPU move
                cpu_move = random.choice(list(move_dict))
                while cpu.mana - move_dict[cpu_move]['cost'] < 0:
                    cpu_move = random.choice(list(move_dict))
                cpu.use_move(cpu_move, move_dict[cpu_move]['cost'])
                
                # Fight commence!
                # Both charge
                if player.status == cpu.status == 'restore':
                    await ctx.send(embed = announce('both_restore', player, cpu))
                # Both defend
                elif player.status == cpu.status == 'defence':
                    await ctx.send(embed = both_defend(player, cpu))
                # Both same attack power
                elif player.status == cpu.status == 'attack' and player.power == cpu.power:
                    if player.move != cpu.move:
                        await ctx.send(embed = announce('diff_attack', player, cpu))
                    else:
                        await ctx.send(embed = announce('same_attack', player, cpu))
                
                # Defend and charge
                elif player.status == 'restore' and cpu.status == 'defence' or cpu.status == 'restore' and player.status == 'defence':
                    await ctx.send(embed = charge_defend(player, cpu))
                
                # Defend and attack
                elif player.status == 'defence' and cpu.status == 'attack' or player.status == 'attack' and cpu.status == 'defence':
                    await ctx.send(embed = defend_attack(player, cpu))
                    
                # Overpowering attacks
                else:
                    await ctx.send(embed = attack_overpower(player, cpu))
            
            if player.status == cpu.status == 'dead':
                print("[ERROR] Something wrong occurred during the fight. Both dead.")
            elif player.status == 'dead':
                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = f"{cpu.name} WINS! :tada:",
                    color = 0xE74C3C # RED
                )
                charge_embed.set_thumbnail(url = self.bot.user.avatar_url)
                await ctx.send(embed = charge_embed)
            elif cpu.status == 'dead':
                charge_embed = discord.Embed(
                    title = 'Charge!',
                    description = f"{player.name} WINS! :tada:",
                    color = 0x2ECC71 # GREEN
                )
                charge_embed.set_thumbnail(url = ctx.message.author.avatar_url)
                await ctx.send(embed = charge_embed)
            else:
                print("[ERROR] Both players are still alive.")


def setup(bot):
    bot.add_cog(Fun(bot))