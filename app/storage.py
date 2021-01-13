"""
Storage Cog Class

This class interacts with the MongoDB database and has methods to store Posts,
and Reminders.
"""

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

    async def add_post(self, ctx, course, name, duedate, handins):
        """
        Adds a new due date posting to the database
        :param ctx: discord ctx object from the command invocation
        :param course: Course string
        :param name: name of the posting
        :param duedate: datetime object representing the time due
        :param handins: list of hand-ins (strings)
        :return: a_id of the resulting post, -1 if the post already exists for a
        given guild
        """
        #Generate the handins list
        guild = ctx.guild.id
        handins_list = []
        if len(handins) == 0:
            handins_list.append("None!")
        else:
            for handin in handins:
                handins_list.append(arg)

        s = course + name + str(guild)
        # Generate the assignment id of 5 digits by hashing the assignment name
        a_id = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**5

        # return -1 so we dont create duplicates
        if await self.post_exists(guild, a_id):
            return -1

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

    async def post_exists(self, guild, a_id):
        """
        Checks if a post with a given a_id exists in the database
        :param guild: int guild id to check existence for
        :param a_id: int a_id to check existence for
        """
        posts = await self.get_posts(guild)
        for post in posts:
            if post['a_id'] == a_id:
                return True
        return False

    async def get_posts(self, guild):
        """
        Retrieves all the posts for a given guild.id
        :param guild: the guild id of the guild to retrieve the posts of
        """
        dates = []
        for post in collection.find({"guild": guild}):
            dates.append(post)
        return dates

    async def update_date(self, guild, a_id, duedate):
        """
        Updates the due date of a given post
        :param guild: guild id the post belongs to
        :param a_id: assingment id of the post
        :param duadate: the new duedate for the post
        """
        result = collection.update_one({"a_id":a_id, "guild":guild}, {"$set":{"duedate":duedate}})
        print("Updated {0}".format(result.inserted_id))

    async def delete_post(self, guild, a_id):
        """
        Deletes a post
        :param guild: guild id the post belongs to
        :param a_id: assingment id of the post
        """
        result = collection.delete_one({"guild":guild, "a_id":a_id})

    def is_past_due(self, post):
        """
        Checks if a given assignment with a_id is past due
        """
        if post["duedate"] < datetime.now():
            return True
        return False

    async def check_for_past_due(self):
        """
        Check through the database for anything considered past due and delete it
        """
        for post in collection.find():
            if self.is_past_due(post):
                await self.delete_post(post["guild"], post["a_id"])

    async def check_reminders(self):
        """
        Checks through all the reminders, and updates any as needed
        :return: a list of reminders that the time has passed for
        """
        past = []
        currenttime = time.time()
        for reminder in reminders.find():
            if reminder["time"] <= currenttime:
                guild = self.bot.get_guild(reminder["guild"])
                channel = guild.get_channel(reminder["channel"])
                for post in reminders.find({"guild":reminder["guild"]}):
                    past.append(post)
                    # now reset the reminder
                quantity_multiplier = helpers.time_in_seconds(reminder["unit"])
                futuretime = int(currenttime + (reminder["interval"] * quantity_multiplier))
                reminders.update_one({"guild":reminder["guild"],"name":reminder["name"]}, {"$set":{"time":futuretime}})
        return past

    # reminders now only send out a string with the name of the reminder, we need a way to
    # give an action to do at each time interval as well
    async def add_reminder(self, guild, channel, time, interval, unit, name):
        """
        Adds a reminder to the database
        :param guild: guild id
        :param channel: channel id to send the reminder to
        :param time: the time in the future to remind at
        :param interval: the interval to remind at, updated whenever the time is in the past
        :param unit: the unit of time
        :param name: name of the reminder
        """
        reminder_data = {
            "guild":guild,
            "channel":channel,
            "time":time,
            "interval":interval,
            "unit":unit,
            "name":name
        }
        result = reminders.insert_one(reminder_data)
        print('One post:{0}'.format(result.inserted_id))

    async def clear_reminders(self, guild):
        """
        Clears all the reminders from the database
        """
        for reminder in reminders.find({"guild":guild}):
            reminders.delete_one({"name": reminder["name"], "guild":guild})

    async def get_reminders(self, guild):
        """
        Gets the Reminders for a given guild
        :param guild: guild id to get the reminders for
        :return: a list of reminders
        """
        remind = []
        for reminder in reminders.find({"guild", guild}):
            remind.append(reminder)
        return remind
