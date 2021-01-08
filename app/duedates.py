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
from storage import Storage

class DueDates(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.track_dates.start()
        self.storage = Storage(bot)

    @commands.command()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.error.CheckFailure):
            await ctx.send("```\n you dont have the role for this command!\n```")

    @commands.command(name="adddate", help="Adds a due date to the list of due dates.\n arg1: class \narg2: name \narg3: date due format: MON D YYYY HH:MM \nEXAMPLE: Jun 1 2020 18:02 (time is optional)")
    async def duedate(self, ctx, arg1, arg2, arg3, *arg4):
        # this is pretty sloppy, ideally we should abstract this behaviour and use regex but this try catch works for now
        try:
            duedatetime = datetime.strptime(arg3, '%b %d %Y %H:%M')
        except ValueError:
            try:
                duedatetime = datetime.strptime(arg3, '%b %d %Y')
            except:
                await ctx.send("Due date could not be parsed")
                return

        a_id = await self.storage.add_post(ctx, arg1, arg2, duedatetime, arg4)
        await ctx.send("```Added Due Date for: " + arg2 + "\nClass:  " + arg1 + "\nDue on: " + duedatetime.strftime('%b %d %Y') + "\nAssignment ID: " + str(a_id) + "\n```" )

    @commands.command(name="dates", help="Lists all due dates")
    async def listalldue(self, ctx):
        posts = await self.storage.get_posts(ctx.guild.id)
        for post in posts:
            await ctx.send(helpers.build_output_string(post))

    @commands.command(name="datesforclass", help="Lists all the due dates for a specified course")
    async def listduefor(self, ctx, arg1):
        posts = await self.storage.get_posts(ctx.guild.id)
        for post in posts:
            if post["class"] == arg1:
                await ctx.send(helpers.build_output_string(post))

    @commands.command(name="duetoday", help="Lists everything due today")
    async def todaydue(self, ctx):
        posts = self.storage.get_posts(ctx.guild.id)
        for post in posts:
            if post["duedate"].date() == ctx.message.created_at.date():
                await ctx.send(helpers.build_output_string(post))

    @commands.command(name="changeduedate", help="Changes the due date of an assigment \narg1: assigment id \narg2: new date with format: MON D YYYY HH:MM \nEXAMPLE: Jun 1 2020 18:02 (time is optional)" )
    async def change_due_date(self, ctx, arg1: int, arg2):
        try:
            duedatetime = datetime.strptime(arg2, '%b %d %Y %H:%M')
        except ValueError:
            try:
                duedatetime = datetime.strptime(arg2, '%b %d %Y')
            except:
                await ctx.send("Due date could not be parsed")
                return
        await self.storage.update_date(ctx.guild.id, arg1, duedatetime)
        await ctx.send("```Updated Assignment with ID {0}```".format(arg1))
        posts = self.storage.get_posts(ctx.guild.id)
        for post in posts:
            if post["a_id"] == arg1:
                await ctx.send(helpers.build_output_string(post))

    @commands.command(name="duethisweek", help="Lists everything due in the next seven days")
    async def due_this_week(self, ctx):
        posts = await self.storage.get_posts(ctx.guild.id)
        time = ctx.message.created_at
        for post in posts:
            timetilldue = post["duedate"] - time
            if timetilldue.days <= 7:
                await ctx.send(helpers.build_output_string(post))

    @commands.command(name="clearhandins", help="clears the hand ins for a given assigment \narg1: assignment id")
    async def clear_handins(self, ctx, arg1: int):
        guild = ctx.guild.id
        emptyduelist = ["None!"]
        collection.update_one({"guild":guild, "a_id":arg1}, {"$set":{"handins":emptyduelist}})
        for post in collection.find({"guild":guild, "a_id":arg1}):
            await ctx.send("```Updated!\n```" + helpers.build_output_string(post))

    @commands.command(name="show", help="returns how long till the given assignment is due. \narg1: class \narg2: name", aliases=["daystilldue"])
    async def days_till_due(self, ctx, arg1, arg2):
        posts = await self.storage.get_posts(ctx.guild.id)
        time = ctx.message.created_at
        for post in posts:
            if post["name"] == arg2 and post["class"] == arg1:
                timetilldue = post["duedate"] - time
                await ctx.send(helpers.build_output_string(post))
                if timetilldue.days <= 0:
                    await ctx.send("```\nDue Today at: " + post["duedate"].strftime("%I:%M%p") +"\n```")
                else:
                    await ctx.send("```\nDue in: " + str(timetilldue.days) + " Days " + str(int(timetilldue.seconds / 3600)) + " Hours\n```")

    @commands.command(name="setreminder", help="set a timed reminder for all assignments that will be sent to the channel you ran this command in\narg1: Time Quantity \narg2: Time Unit (only days supported right now) \narg3: name of the reminder")
    async def set_reminder(self, ctx, arg1: int, arg2: str, arg3):
        quantity_multiplier = helpers.time_in_seconds(arg2)
        futuretime = int(time.time() + (arg1 * quantity_multiplier))
        await self.storage.add_reminder(ctx.guild.id, ctx.channel.id, futuretime, arg1, arg2, arg3)
        await ctx.send("```\nAdded Reminder " + arg3 + " for every " + str(arg1) + " " + arg2 + "\n```")

    @commands.command(name="listreminders", help="lists all reminders")
    async def list_reminders(self, ctx):
        reminders = await self.storage.get_reminders(ctx.guild.id)
        for reminder in reminders:
            await ctx.send("```\nReminder: " + reminder["name"] + "\nInterval: " +
            str(reminder["interval"]) +" " + reminder["unit"] +"\nTo Channel:" + ctx.guild.get_channel(reminder["channel"]).name + "\n```")

    @commands.command(name="clearreminders", help="clears all reminders")
    async def clear_reminders(self, ctx):
        await self.storage.clear_reminders(ctx.guild.id)
        await ctx.send("```Cleared reminders```")

    @commands.command(name="bulkadd", help="bulkadds assignments from a csv attached to the command message\n CVS header format: class, name, date, handins\n handins should be a spaces seperated list")
    async def bulk_add(self, ctx):
        bulk_list_url = ""
        for file in ctx.message.attachments:
            bulk_list_url = file.url
        response = requests.get(bulk_list_url)
        lines = response.text.splitlines()
        reader = csv.DictReader(lines)
        self.storage.bulk_add(reader)

    @tasks.loop(seconds=30.0)
    async def track_dates(self):
        print("Checking Reminders")
        # this behaviour should be abstracted
        reminders = await self.storage.check_reminders()
        if reminders:
            for reminder in reminders:
                guild = self.bot.get_guild(reminder["guild"])
                channel = guild.get_channel(reminder["channel"])
                await channel.send("```\nReminder: " + reminder["name"] + "\nInterval: " +
                str(reminder["interval"]) +" " + reminder["unit"] + "\n```")

        print("Checking for Past Due Posts")
        await self.storage.check_for_past_due()

    @track_dates.before_loop
    async def before_track_dates(self):
        await self.bot.wait_until_ready()

def setup(bot):
    b = DueDates(bot)
    bot.add_cog(b)
