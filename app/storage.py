import os
import pymongo
from datetime import datetime
import time
import json
from pymongo import MongoClient
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import hashlib
import asyncio

import helpers

DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
collection = db["duedates"]
reminders = db["reminders"]

class Storage(commands.Cog):
    """
    Storage Object
    this object directly queries the MongoDB database using the pymongo library.
    This class should be the only class that interacts with the database directly
    """

    def __init__(self, bot):
        self.bot = bot

    async def add_date(self, ctx, course, name, duedate, handins):
        """
        Adds a new due date posting to the database
        :param ctx: discord ctx object from the command invocation
        :param course: Course string
        :param name: name of the posting
        :param duedate: datetime object representing the time due
        :param handins: list of hand-ins (strings)
        :return: a_id of the resulting post
        """
        #Generate the handins list
        guild = ctx.guild.id
        handins_list = []
        if len(handins) is 0:
            handins_list.append("None!")
        else:
            for handin in handins:
                handins_list.append(arg)

        s = course + name + str(guild)
        #Generate the assignment id of 4 digits by hashing the assignment name
        a_id = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**4

        #add the new assignment to the database
        post_data = {
            'guild': guild,
            'name': name,
            'class': course,
            'a_id': a_id,
            'duedate': duedate,
            'handins': handins_list
        }
        result = collection.insert_one(post_data)
        print('One post:{0}'.format(result.inserted_id))
        return a_id

    async def list_due(self, ctx):
        dates = []
        guild = ctx.guild.id
        for post in collection.find({"guild": guild}):
            dates.append(helpers.build_output_string(post))
        return dates

    async def bulk_add(self, reader):
        duedates = self.bot.get_cog('DueDates')
        for row in reader:
            if row['handins'] is not None:
                handins = tuple(map(str, row['handins'].split()))
            else:
                handins = []
            await add_date(ctx, row['class'], row['name'], row['date'], *handins)
