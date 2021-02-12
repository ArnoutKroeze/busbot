import aiohttp
import asyncio
import os
import random

import discord
from discord import File
from discord.ext import commands

from backend import biernet

klok_dir = "~/Media/klok_memes/"

async def on_message_bier(self, message: discord.message):
    proost = ["bier", "bus", "bussen", "drinken", "pils", "slok", "slokken", "drankje"]
    bericht = message.content.lower()
    if any(woord in bericht for woord in proost):
        await message.add_reaction(emoji="\U0001F37B")
    return


class Leuk(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.author.bot:
            return
        await on_message_bier(self, message)

    @commands.command(name="klok", aliases=["klonk", "meme"])
    async def stuur_klokmeme(self, ctx):
        """
        Stuur een lekkere lauwe klokmeme
        """

        #hier zijn klok_memes
        klok_memes_dir = [f for f in os.listdir(klok_dir)]
        klok_meme = random.choice(klok_memes_dir)
        with open(os.path.join(klok_dir, klok_meme), "rb") as f:
            picture = discord.File(f)
            await ctx.send(file=picture)

    @commands.command(name="biernet", aliases=['bier', 'beer'], brief="Geeft de huidige bieraanbiedingen voor je!")
    async def doe_biernet(self, ctx, *args):
        """
        Find the best deal for a (crate of) beer on biernet.nl
        """
        channel = ctx.channel

        text = ''.join(args[i] + ' ' for i in range(0, len(args)))
        text = text.strip()

        if text == "":
            message = "Usage: !bier [bier merk]"
            await ctx.send("Zet er ff een biermerk achter, dat helpt")

        if "heineken" in text.lower():
            await ctx.send("*Heikenen, bah")
            await ctx.message.add_reaction(emoji="\U0001F92E")
            return

        if "bavaria" in text.lower():
            await ctx.send("*Beffaria, bah")
            await ctx.message.add_reaction(emoji="\U0001F92E")
            return

        if "amstel" in text.lower():
            await ctx.send("ewww")
            await ctx.message.add_reaction(emoji="\U0001F92E")
            return

        try:
            # Search biernet for the provided beer
            result = await biernet.search(ctx, text)
            # Create an embed with the results
            embed: discord.Embed = discord.Embed(
                title='De goedkooptste verkoper van ' + result['brand'], url=result['url'],
                colour=discord.colour.Colour.green(),
                description=result['name'])
            embed.add_field(name=result['product'],  inline=True,
                            value="~~" + result['original_price'] + "~~ **" + result['sale_price'] + "**")
            embed.add_field(name=result['PPL'], inline=True, value=result['sale'])
            embed.set_author(name=result['shop_name'], url=result['biernet_shop_url'], icon_url=result['shop_img'])
            embed.set_thumbnail(url=result['img'])
            embed.set_footer(text="Tot " + result['end_date'],
                            icon_url="https://biernet.nl/site/images/general_site_specific/logo-klein.png")
            await channel.send(embed=embed)
        except aiohttp.ClientConnectorError:
            await channel.send("Is biernet stuk? Ik kom er niet bij")
        except ValueError as e:
            await channel.send(str(e))

        return


def setup(bot):
    bot.add_cog(Leuk(bot))
