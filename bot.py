import os
import pymongo
import datetime
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

@bot.command(name="add-due-date", help="Adds a due date to the list of due dates")
async def duedate(ctx, arg1, arg2, arg3):
    post_data = {
        'name': arg1 ,
        'class': arg2,
        'duedate': arg3
    }
    result = collection.insert_one(post_data)
    print('One post:{0}'.format(result.inserted_id))
    await ctx.send("Added Due Date for: " + arg1 + "\nClass:  " + arg2 + "\nDue on: " + arg3)

@bot.command(name="list-due-dates", help="Lists all due dates")
async def listdue(ctx):
    duedates = []
    for post in collection.find():



bot.run(TOKEN)
