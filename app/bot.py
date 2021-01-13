import os, sys, traceback
import pymongo
from datetime import datetime
import json
from pymongo import MongoClient
import discord
from discord.ext import commands
from dotenv import load_dotenv
import hashlib

import helpers
"""
    Bot entry point. Loads all the cogs into the bot then starts the bot
"""

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='@', description="A Bot for the CMPT Study groups discord")
initial_extensions = ["duedates", "studygroup"]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for guild in bot.guilds:
        print(guild.name + ": " + str(guild.id))

bot.run(TOKEN)
