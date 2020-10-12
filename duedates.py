import os
import pymongo
from datetime import datetime
import time
import json
from pymongo import MongoClient
import discord
from discord.ext import commands
from dotenv import load_dotenv
import hashlib
import asyncio

import helpers

DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
collection = db["duedates"]
reminders = db["reminders"]

class DueDatesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.error.CheckFailure):
            await ctx.send("```\n you dont have the role for this command!\n```")

    @commands.command(name="adddate", help="Adds a due date to the list of due dates.\n arg1: class \narg2: name \narg3: date due format: MON D YYYY HH:MM \nEXAMPLE: Jun 1 2020 18:02 (time is optional)")
    async def duedate(self, ctx, arg1, arg2, arg3, *arg4):
        # this is pretty sloppy, ideally we should abstract this behaviour and use regex but this try catch works for now
        try:
            duedatetime = datetime.strptime(arg3, '%b %d %Y %H:%S')
        except ValueError:
            try:
                duedatetime = datetime.strptime(arg3, '%b %d %Y')
            except:
                await ctx.send("Due date could not be parsed")
                return

        guild = ctx.guild.id

        #Generate the handins list
        handins = []
        print(str(len(arg4)) + str(arg4))
        if len(arg4) is 0:
            handins.append("None!")
        else:
            for arg in arg4:
                handins.append(arg)

        s = arg1 + arg2 + str(guild)
        #Generate the assignment id of 4 digits by hashing the assignment name
        a_id = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**4

        #add the new assignment to the database
        post_data = {
            'guild': guild,
            'name': arg2,
            'class': arg1,
            'a_id': a_id,
            'duedate': duedatetime,
            'handins': handins
        }
        result = collection.insert_one(post_data)
        print('One post:{0}'.format(result.inserted_id))

        handinstring = ""
        for handin in handins:
            handinstring += "-" + handin + "\n"

        await ctx.send("```Added Due Date for: " + arg2 + "\nClass:  " + arg1 + "\nDue on: " + duedatetime.strftime('%b %d %Y') + "\nHand-ins:\n " + handinstring + "\nAssignment ID: " + str(a_id) + "\n```" )

    @commands.command(name="dates", help="Lists all due dates")
    async def listalldue(self, ctx):
        dates = []
        guild = ctx.guild.id
        for post in collection.find({"guild": guild}):
            dates.append(helpers.build_output_string(post))

        for date in dates:
            await ctx.send(date)

    @commands.command(name="datesforclass", help="Lists all the due dates for a specified course")
    async def listduefor(self, ctx, arg1):
        dates = []
        guild = ctx.guild.id
        for post in collection.find({"guild": guild ,"class":arg1}):
            dates.append(helpers.build_output_string(post))

        for date in dates:
            await ctx.send(date)

    @commands.command(name="duetoday", help="Lists everything due today")
    async def todaydue(self, ctx):
        dates = []
        guild = ctx.guild.id
        currenttime = ctx.message.created_at
        for post in collection.find({"guild": guild}):
            if post["duedate"].date() == currenttime.date():
                dates.append(helpers.build_output_string(post))

        for date in dates:
            await ctx.send(date)

    @commands.command(name="addhandins", help="allows you to add a list of hand ins to a given due date item\narg1: Assignment ID\nArg2: Hand-ins to add")
    async def addhandin(self, ctx, arg1: int, *arg2):
        if len(arg2) is 0:
            await ctx.send("```You didn't give any new hand-ins to add!```")
            return
        guild = ctx.guild.id
        handins = []
        db_handins = []

        for post in collection.find({"guild":guild}):
            if post["a_id"] == arg1:
                db_handins = post['handins']
                for handin in db_handins:
                    if handin == "None!":
                        pass
                    else:
                        handins.append(handin)
                for arg in arg2:
                    if arg not in db_handins:
                        handins.append(arg)
                collection.update_one({"a_id":arg1, "guild":guild}, {"$set":{"handins":handins}})
        for post in collection.find({"guild":guild, "a_id":arg1}):
            await ctx.send("```Updated!\n```" + helpers.build_output_string(post))

    @commands.command(name="delete", help="Deletes an assigment by id \narg1: Assigment ID")
    async def remove_hand_in(self, ctx, arg1: int):
        guild = ctx.guild.id
        collection.delete_one({"guild":guild, "a_id":arg1})
        await ctx.send("```\nDeleted Assignment with id: " + str(arg1) + "\n```")

    @commands.command(name="deletepastdue", help="Deletes all assignments that are past due")
    async def remove_past_due(self, ctx):
        guild = ctx.guild.id
        for post in collection.find({"guild":guild}):
            timedel = post["duedate"] - datetime.now()
            if timedel.days < 0:
                await ctx.send("Deleted: " + post["class"] + " " + post["name"])
                collection.delete_one({"guild":guild, "a_id": post["a_id"], "class": post["class"]})

    @commands.command(name="changeduedate", help="Changes the due date of an assigment \narg1: assigment id \narg2: new date with format: MON D YYYY HH:MM \nEXAMPLE: Jun 1 2020 18:02 (time is optional)" )
    async def change_due_date(self, ctx, arg1: int, arg2):
        guild = ctx.guild.id
        try:
            duedatetime = datetime.strptime(arg2, '%b %d %Y %H:%S')
        except ValueError:
            try:
                duedatetime = datetime.strptime(arg2, '%b %d %Y')
            except:
                await ctx.send("Due date could not be parsed")
                return

        collection.update_one({"a_id":arg1, "guild":guild}, {"$set":{"duedate":duedatetime}})
        for post in collection.find({"guild":guild, "a_id":arg1}):
            await ctx.send("```Updated!\n```" + helpers.build_output_string(post))

    @commands.command(name="duethisweek", help="Lists everything due in the next seven days")
    async def due_this_week(self, ctx):
        guild = ctx.guild.id
        time = ctx.message.created_at
        for post in collection.find({"guild":guild}):
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

    @commands.command(name="daystilldue", help="returns how long till the given assignment is due. \narg1: class \narg2: name")
    async def days_till_due(self, ctx, arg1, arg2):
        guild = ctx.guild.id
        time = ctx.message.created_at
        for post in collection.find({"guild":guild}):
            if post["name"] == arg2 and post["class"] == arg1:
                timetilldue = post["duedate"] - time
                await ctx.send(helpers.build_output_string(post))
                if timetilldue.days <= 0:
                    await ctx.send("```\nDue Today at: " + post["duedate"].strftime("%I:%M%p") +"\n```")
                else:
                    await ctx.send("```\nDue in: " + str(timetilldue.days) + " Days " + str(int(timetilldue.seconds / 3600)) + " Hours\n```")

    @commands.command(name="show", help="prints out the details of a specific assignment \narg1: class \narg2: name")
    async def show_assign(self, ctx, arg1, arg2):
        guild = ctx.guild.id
        for post in collection.find({"guild":guild}):
            if post["name"] == arg2 and post["class"] == arg1:
                await ctx.send(helpers.build_output_string(post))

    @commands.command(name="setreminder", help="set a timed reminder for all assignments that will be sent to the channel you ran this command in\narg1: Time Quantity \narg2: Time Unit (only days supported right now) \narg3: name of the reminder", hidden=True)
    async def set_reminder(self, ctx, arg1: int, arg2: str, arg3):
        guild = ctx.guild.id
        channel = ctx.channel.id
        quantity_multiplier = 1
        if "Days" in arg2 or "days" in arg2:
            quantity_multiplier = 86400
        #seconds is here for testing
        if "Seconds" in arg2 or "seconds" in arg2:
            quantity_multiplier = 1

        futuretime = int(time.time() + (arg1 * quantity_multiplier))
        reminder_data = {
            "guild":guild,
            "channel":channel,
            "time":futuretime,
            "interval":arg1,
            "unit":arg2,
            "name":arg3
        }
        result = reminders.insert_one(reminder_data)
        print('One post:{0}'.format(result.inserted_id))
        await ctx.send("```\nAdded Reminder " + arg3 + " for every " + str(arg1) + " " + arg2 + "\n```")

    @commands.command(name="removereminders", help="removes all reminders", hidden=True)
    async def remove_reminders(self, ctx):
        guild = ctx.guild.id
        for reminder in reminders.find({"guild":guild}):
            reminders.delete_one({"name":reminder["name"]})
        await ctx.send("```\nRemoved all reminders!\n```")

    @commands.command(name="listreminders", help="lists all reminders", hidden=True)
    async def list_reminders(self, ctx):
        guild = ctx.guild.id
        for reminder in reminders.find({"guild":guild}):
            await ctx.send("```\nReminder: " + reminder["name"] + "\nInterval: " +
            str(reminder["interval"]) +" " + reminder["unit"] +"\nTo Channel:" + ctx.guild.get_channel(reminder["channel"]).name + "\n```")

    async def reminders(self):
        while self is self.bot.get_cog("DueDatesCog"):
            currenttime = time.time()
            # only do this if we are connected!
            if self.bot.guilds:
                for reminder in reminders.find():
                    # check if the reminder time is in the past
                    if reminder["time"] <= currenttime:
                        guild = self.bot.get_guild(reminder["guild"])
                        channel = guild.get_channel(reminder["channel"])
                        await channel.send("```\nReminder!\n```")
                        for post in collection.find({"guild":reminder["guild"]}):
                            await channel.send(helpers.build_output_string(post))
                            # now reset the reminder
                            quantity_multiplier = 1
                            if "Days" in reminder["unit"] or "days" in reminder["unit"]:
                                quantity_multiplier = 86400
                            #seconds is here for testing
                            if "Seconds" in reminder["unit"] or "seconds" in reminder["unit"]:
                                quantity_multiplier = 1
                            futuretime = int(currenttime + (reminder["interval"] * quantity_multiplier))
                        reminders.update_one({"guild":reminder["guild"],"name":reminder["name"]}, {"$set":{"time":futuretime}})
            await asyncio.sleep(10)

def setup(bot):
    b = DueDatesCog(bot)
    eloop = asyncio.get_event_loop()
    eloop.create_task(b.reminders())
    bot.add_cog(b)
