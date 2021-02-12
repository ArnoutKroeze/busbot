#!
import json
import aiohttp
from json import JSONDecodeError

import discord
from discord.ext import commands

config_file = "config.json"
prefix_file = "prefixes.json"

if __name__ == "__main__":
    #with open("README.md", "r") as file:
    #    help_message = "".join(file.readlines())

    with open(config_file, "r") as file:
        data = json.load(file)
        TOKEN = data['token']
        ADMIN = data['admin']


def get_prefix(_: commands.Bot, message: discord.Message):
    # ja dit kan vast beter
    with open(prefix_file, "w+") as f:
        try:
            prefixes = json.load(f)
            return prefixes[str(message.guild.id)]
        except JSONDecodeError:
            prefixes = {}
            prefixes[str(message.guild.id)] = "!"
            json.dump(prefixes, f, indent=4)
            return "!"
        except KeyError as e:
            prefixes[str(message.guild.id)] = "!"
            json.dump(prefixes, f, indent=4)
            return "!"


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)


@bot.event
async def on_guild_remove(guild):
    with open(prefix_file, "w") as f:
        prefixes = json.load(f).pop(str(guild.id))
        json.dump(prefixes, f, indent=4)


@bot.command(name="changeprefix_busbot")
async def change_prefix(ctx, new_prefix: str):
    if len(new_prefix) >= 4:
        await ctx.send("Doe maar iets wat max 3 tekens lang is")
    else:
        with open(prefix_file, "w+") as f:
            prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = new_prefix
            json.dump(prefixes, f, indent=4)


@bot.event
async def on_ready():
    bot._session = aiohttp.ClientSession() # to do internet things

    print(f"Logged in as: {bot.user.name}")
    print(f"Ik ben in {len(bot.guilds)} servers")

if __name__ == "__main__":
    extensions = ["cogs.leuke_dingen",
                  "cogs.bussen"]

    [bot.load_extension(ext) for ext in extensions]
    bot.run(TOKEN)


