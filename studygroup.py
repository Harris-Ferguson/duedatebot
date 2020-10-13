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

DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
users = db["users"]

class StudyGroupCog(commands.Cog):

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

            exists = await is_in_db(ctx.author.id)
            if exists:
                count = 0
                for user in users.find({"user_id":ctx.author.id}):
                    count = user["mikes"] + 1
                users.update_one({"user_id":ctx.author.id}, {"$set":{"mikes":count}})
            else:
                await add_user(ctx)

    @commands.command(hidden=True)
    async def add_user(self, ctx):
        guild = ctx.guild.id
        user_id = ctx.author.id

        user_data = {
            "guild":guild,
            "user_id":user_id,
            "mikes":0
        }
        result = users.insert_one(user_data)
        print('Added User:{0}'.format(result.inserted_id))

    @commands.command(name="leaderboard", help="I was keeping track the whole time")
    async def top_5(self, ctx):
        everyone = {}
        for user in users.find({"guild":ctx.guild.id}):
            name = ctx.guild.get_member(user["user_id"]).display_name
            everyone[name] = user["mikes"]
        leaderboard = dict(sorted(everyone.items(), key=operator.itemgetter(1), reverse=True))
        print(leaderboard)

    @commands.command(hidden=True)
    def is_in_db(self, id):
        if users.find({"user":id}).count() > 0:
            return True
        else:
            return False


def setup(bot):
    bot.add_cog(StudyGroupCog(bot))
