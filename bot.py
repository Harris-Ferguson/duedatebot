import os
import pymongo
from datetime import datetime
import json
from pymongo import MongoClient
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DBPASS = os.getenv('DB_PASS')

cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = cluster["duedates"]
collection = db["duedates"]

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="duedates")
async def duedate(ctx):
    await ctx.send("hello!")

@bot.command(name="add-due-date", help="Adds a due date to the list of due dates.\n arg1: name arg2: class arg3: date due format: MON D YYYY EXAMPLE: Jun 1 2020")
async def duedate(ctx, arg1, arg2, arg3):
    duedatetime = datetime.strptime(arg3, '%b%d%Y')
    post_data = {
        'name': arg1,
        'class': arg2,
        'duedate': duedatetime
    }
    result = collection.insert_one(post_data)
    print('One post:{0}'.format(result.inserted_id))
    await ctx.send("Added Due Date for: " + arg1 + "\nClass:  " + arg2 + "\nDue on: " + duedatetime.strftime('%b %d %Y'))

@bot.command(name="list-due-dates", help="Lists all due dates")
async def listdue(ctx):
    dates = []
    for post in collection.find():
        dates.append(post["class"] + " " + post["name"] + " Due On: " + post["duedate"].strftime('%b %d %Y'))

    for date in dates:
        await ctx.send(date)

bot.run(TOKEN)
