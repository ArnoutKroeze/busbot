import asyncio
import random

import discord
from discord.ext import commands

from backend.bussen import Bussen
from cogs.leuke_dingen import on_message_bier

games = {}


def get_game(channel_id):
    try:
        return games[channel_id]
    except KeyError:
        return None


class Busbot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):

        if message.author.bot:
            return

        game = get_game(message.channel.id)

        if game is None:
            return
        else:
            output = game.play(message.content.lower(), message.author)
            if game.game_status >= 6:
                games.pop(message.channel.id)
            if output:
                await message.channel.send(output)

                # add bier reactie als degene moet drinken, of slokken mag uitdelen
                proost = ["bier", "bus", "bussen", "drinken", "pils", "slok", "slokken"]
                if any(woord in output for woord in proost):
                    await message.add_reaction(emoji="\U0001F37B")

    @commands.command(name="join", aliases=["meedoen", "ik", "ikke", "ikkuh", "jonko", "ja"])
    async def join(self, ctx):
        game = get_game(ctx.channel.id)
        user = ctx.author
        channel = ctx.channel
        if game is None:
            # Maak een spel aan
            games[channel.id] = Bussen()
            get_game(channel.id).join(user.id, user.display_name)
            await ctx.send(f"ooh yes we gaan lekker bussen met {user.display_name}! Wie doen er nog meer mee?")
        elif user.id in [player.id for player in game.players]:
            await ctx.send("je doet al mee, gek")
        elif game.started:
            await ctx.send("We zijn al begonnen hiero, ff wachten")
        elif len(game.players) >= 7:
            await ctx.send("Ik heb arbitrair gekokzen dat er maar 7 mensen kunnen meedoen,(en jij bent de achtste) "
                           "omdat er anders te weinig kaarten in het spel blijven ofzo")
        else:
            game.join(user.id, user.display_name)
            await ctx.send(f"Leuk dat je meedoet {user.display_name}! Wie doen er nog meer mee?")

        return

    @commands.command(name="start", aliases=["begin"], brief="start the game when people joined")
    async def start(self, ctx):
        channel = ctx.channel
        game = get_game(channel.id)
        if game:
            if not game.started:
                output = game.play(initiate=True)
            else:
                output = "We zijn al bezig, gek"
        else:
            output = "Je kunt geen spel doen zonder spelers! join eerst"

        if output:
            await channel.send(output)

    @commands.command(name="leave", brief="Leave the game")
    async def leave(self, ctx):
        channel = ctx.channel
        game = get_game(channel.id)
        if game:
            output, end_game = game.leave(ctx.author.id)
            if end_game:
                games.pop(channel.id)
        else:
            output = "Er is niet eens een spel of te verlaten"

        await channel.send(output)

    @commands.command(name="end", aliases=["eind", "stop"], brief="End the game for everyone")
    async def end(self, ctx):
        channel = ctx.channel

        if not get_game(channel.id):
            await channel.send("Er is hier niks gaande")
            return

        games.pop(channel.id)
        output = random.choice(["ik adviseer je een glaasje water te drinken",
                                "ik adviseer je nog een potje te doen",
                                "de volgende ronde met sterke drank?"])

        await channel.send(output)

    @commands.command(name="wie", brief="Laat zien wie er momenteel meedoen")
    async def wie(self, ctx):
        game = get_game(ctx.channel.id)
        leden = [speler.name for speler in game.players]
        output = "\n".join(leden)
        await ctx.send(output)


    @commands.command(name="cards", aliases=["kaarten"], brief="Shows your handcards")
    async def show_cards(self, ctx):
        channel = ctx.channel

        if not get_game(channel.id):
            output = "je moet wel meedoen om kaarten te hebben"
            await channel.send(output)
            return

        output = get_game(channel.id).show_cards(ctx.author)

        await channel.send(output)

        return


def setup(bot):
    bot.add_cog(Busbot(bot))
