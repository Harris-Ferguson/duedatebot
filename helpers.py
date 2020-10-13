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
    "\n< Due On: " + post["duedate"].strftime('%b %d %Y %I:%S %p') + " >\nHand-Ins:\n" + h + "```"


def is_in_db(name):
    if users.find({"name":name}).count() > 0:
        return True
    else:
        return False
