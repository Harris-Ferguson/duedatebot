"""
This defines a class of commands specifically for the CMPT study groups discord
"""
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

class StudyGroupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mike", help="just for fun")
    async def mike(self, ctx):
        guildname = ctx.guild.name
        if guildname == "CMPT Study Groups":
            emojis = ctx.guild.emojis
            mikes = []
            for emoji in emojis:
                if emoji.name in "Mike" or emoji.name == "HolUp":
                    mikes.append(emoji)
            pick = random.randomint(0,len(mikes))
            await ctx.send(str(mikes[pic]))
            return

def setup(bot):
    bot.add_cog(StudyGroupCog(bot))
