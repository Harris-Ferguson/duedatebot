import os
import pymongo
from datetime import datetime
import json
from pymongo import MongoClient
import discord
from discord.ext import commands
from dotenv import load_dotenv

import helpers

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DBPASS = os.getenv('DB_PASS')

cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = cluster["duedates"]
collection = db["duedates"]

bot = commands.Bot(command_prefix='@')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("```Someone is trying something illegal! (you need admin for this command)```")

@bot.command(name="adddate", help="Adds a due date to the list of due dates.\n arg1: name arg2: class arg3: date due format: MON D YYYY EXAMPLE: Jun 1 2020")
@commands.has_role("admin")
async def duedate(ctx, arg1, arg2, arg3, *arg4):
    duedatetime = datetime.strptime(arg3, '%b%d%Y')
    guild = ctx.guild.id
    handins = []

    if len(arg4) is 0:
        handins.append("None!")
    else:
        for arg in arg4:
            handins.append(arg)

    print("Hello")
    post_data = {
        'guild': guild,
        'name': arg1,
        'class': arg2,
        'duedate': duedatetime,
        'handins': handins
    }
    result = collection.insert_one(post_data)
    print('One post:{0}'.format(result.inserted_id))

    #this builds a string for the handins, this could probably be a list comprehension but I'm too lazy
    handinstring = ""
    for handin in handins:
        handinstring += handin + " "

    await ctx.send("```Added Due Date for: " + arg1 + "\nClass:  " + arg2 + "\nDue on: " + duedatetime.strftime('%b %d %Y') + "\nHand-ins: " + handinstring + "```")

@bot.command(name="dates", help="Lists all due dates")
async def listalldue(ctx):
    dates = []
    guild = ctx.guild.id
    for post in collection.find({"guild": guild}):
        dates.append(helpers.build_output_string(post))

    for date in dates:
        await ctx.send(date)

@bot.command(name="datesforclass", help="Lists all the due dates for a specified course")
async def listduefor(ctx, arg1):
    dates = []
    guild = ctx.guild.id
    for post in collection.find({"guild": guild ,"class":arg1}):
        dates.append(helpers.build_output_string(post))

    for date in dates:
        await ctx.send(date)

@bot.command(name="duetoday", help="Lists everything due today")
async def todaydue(ctx):
    dates = []
    guild = ctx.guild.id
    for post in collection.find({"guild": guild}):
        if post["duedate"].date() == datetime.today().date():
            dates.append(helpers.build_output_string(post))

    for date in dates:
        await ctx.send(date)

bot.run(TOKEN)
