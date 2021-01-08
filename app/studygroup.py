"""
This defines a class of commands specifically for the CMPT study groups discord
"""
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import os
from pymongo import MongoClient
from operator import itemgetter
import operator

import helpers

DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
users = db["users"]

class StudyGroup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mike", help="just for fun")
    async def mike(self, ctx):
        guildname = ctx.guild.name
        if guildname == "CMPT Study Groups":
        # print the emoji first
            emojis = ctx.guild.emojis
            mikes = []
            for emoji in emojis:
                if "Mike" in emoji.name or emoji.name == "HolUp":
                    mikes.append(emoji)
            pick = random.randint(0,len(mikes) - 1)
            await ctx.send(str(mikes[pick]))

            if helpers.is_in_db(ctx.author.display_name):
                count = 0
                for user in users.find({"name":ctx.author.display_name}):
                    count = user["mikes"] + 1
                users.update_one({"name":ctx.author.display_name}, {"$set":{"mikes":count}})
            else:
                await ctx.invoke(self.bot.get_command("add_user"))

    @commands.command(hidden=True)
    async def add_user(self, ctx):
        guild = ctx.guild.id
        user = ctx.author.display_name

        user_data = {
            "guild":guild,
            "name":user,
            "mikes":1
        }
        result = users.insert_one(user_data)
        print('Added User:{0}'.format(result.inserted_id))

    @commands.command(name="leaderboard", help="I was keeping track the whole time")
    async def top_5(self, ctx):
        await ctx.send("```\nMike Leaderboard!```")
        everyone = {}
        for user in users.find({"guild":ctx.guild.id}):
            everyone[user["name"]] = user["mikes"]

        leaderboard = dict(sorted(everyone.items(), key=operator.itemgetter(1), reverse=True))
        for user, mikes in leaderboard.items():
            await ctx.send('```fix\n' + user + ": " + str(mikes)  + '\n```')

def setup(bot):
    bot.add_cog(StudyGroup(bot))
