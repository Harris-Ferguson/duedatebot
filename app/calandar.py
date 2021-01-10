from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import discord
from discord.ext import commands
import asyncio

import helpers
from storage import Storage

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class Calandar(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.storage = Storage(bot)

        def get_creds(self):
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            return creds

        @commands.command(name="createcalendar")
        async def create_cal(self, ctx):
            creds = self.get_creds()
            service = build('calendar', 'v3', credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                await ctx.send("No events found!")
            for event in events:
                await ctx.send(str(event["summary"]))

def setup(bot):
    b = Calandar(bot)
    bot.add_cog(b)
