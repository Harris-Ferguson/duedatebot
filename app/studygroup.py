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
import requests
import chess
import chess.svg
import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

import helpers

# this needs to be rewritten to use the new storage object, but its
# not part of the bot "proper", rather its a set of fun commands for our
# specific study group / school discord, so its not a huge deal if its not
# strict

DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
users = db["users"]

class StudyGroup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.chess_url = "https://api.chess.com/pub/"

    @commands.command(name="mike", help="just for fun")
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def mike(self, ctx):
        guild_id = ctx.guild.id
        if guild_id == 750992924539486275:
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
    @commands.cooldown(1, 6000, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def top_5(self, ctx):
        channel_name = ctx.channel.name
        await ctx.send("```\nMike Leaderboard!```")
        everyone = {}
        for user in users.find({"guild":ctx.guild.id}):
            everyone[user["name"]] = user["mikes"]

        leaderboard = dict(sorted(everyone.items(), key=operator.itemgetter(1), reverse=True))
        for user, mikes in leaderboard.items():
            await ctx.send('```fix\n' + user + ": " + str(mikes)  + '\n```')

    @commands.command(name="puzzle", help="chess.com daily puzzle")
    async def puzzle(self, ctx):
        response = requests.get(self.chess_url + "puzzle")
        if response.status_code == 200:
            content = response.json()
            output = content["title"] + "\n Chess.com link: " + content["url"]
            fen = content["fen"]
            board = chess.Board(fen)
            boardsvg = chess.svg.board(board=board)
            f = open("puzzleboard.svg", "w")
            f.write(boardsvg)
            f.close()
            drawing = svg2rlg("puzzleboard.svg")
            renderPM.drawToFile(drawing, "puzzleboard.png", fmt="PNG")
            await ctx.send(output)
            await ctx.send(file=discord.File("puzzleboard.png"))

def setup(bot):
    bot.add_cog(StudyGroup(bot))
