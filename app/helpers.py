"""
Helper functions for the bot
"""
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

load_dotenv()
DBPASS = os.getenv('DB_PASS')
cluster = MongoClient("mongodb+srv://duckypotato:" + DBPASS + "@cluster0.bore2.mongodb.net/duedates?retryWrites=true&w=majority")
db = cluster["duedates"]
users = db["users"]
collection = db["duedates"]
reminders = db["reminders"]

def build_output_string(post):
    """
    Builds an output string to be displayed to the guild. Gives all the information
    of the given post, which is a document in the database
    Issues:
        - This function will fail if the handins field is empty. They are enforced to contain at least one element by the
          duedate function, however we should fix this to consider an empty field
    """
    handins = post['handins']
    h = ''
    for handin in handins:
        h = h + "* " + handin + "\n"

    return "```md\n> Assignment ID: " + str(post["a_id"]) + "\n# " + post["class"] + "\n# " + post["name"] + \
    "\n< Due On: " + post["duedate"].strftime('%b %d %Y %I:%M %p') + " >\nHand-Ins:\n" + h + "```"

def time_in_seconds(time):
    """
    Converts a string unit of time (days, weeks, etc) to an integer number of seconds
    """
    if "years" in time.lower() or "year" in time.lower():
        quantity_multiplier = 31536000 # 86400 * 365
    elif "months" in time.lower() or "month" in time.lower():
        quantity_multiplier = 2592000 # 86400 * 30
    elif "weeks" in time.lower() or "week" in time.lower():
        quantity_multiplier = 604800 # 86400 * 7
    elif "days" in time.lower() or "day" in time.lower():
        quantity_multiplier = 86400
    elif "minutes" in time.lower() or "minute" in time.lower():
        quantity_multiplier = 60
    elif "seconds" in time.lower():
        quantity_multiplier = 1
    return quantity_multiplier

def is_in_db(name):
    """
    Returns true if a given users display name is in the database of users
    """
    if users.find({"name":name}).count() > 0:
        return True
    else:
        return False
