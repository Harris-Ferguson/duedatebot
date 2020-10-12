import os
import pymongo
from pymongo import MongoClient
import discord
from discord.ext import commands
from dotenv import load_dotenv
import csv
import requests
import helpers

class BulkAddCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bulkadd", help="bulkadds assignments from a csv attached to the command message")
    async def bulk_add(self, ctx):
        bulk_list_url = ""
        for file in ctx.message.attachments:
            bulk_list_url = file.url
        response = requests.get(bulk_list_url)
        lines = response.text.splitlines()
        reader = csv.DictReader(lines)

        duedates = self.bot.get_cog('DueDatesCog')
        for row in reader:
            print(row['class'], row['name'], row['date'], row['handins'])
            if row['handins'] is not None:
                handins = tuple(map(str, row['handins'].split()))
            else:
                handins = []
            await duedates.duedate(ctx, row['class'], row['name'], row['date'], *handins)

def setup(bot):
    bot.add_cog(BulkAddCog(bot))
