from __future__ import print_function
from datetime import datetime, timedelta
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
SCOPES = ['https://www.googleapis.com/auth/calendar']

class Calandar(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.storage = Storage(bot)
            self.creds = self.get_creds()

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

        @commands.command(name="createcalendar", help="arg1: name")
        async def create_cal(self, ctx, name):
            # call the google calendar API
            service = build('calendar', 'v3', credentials=self.creds)
            # get the list of reminders
            posts = await self.storage.get_posts(ctx.guild.id)

            # create the calendar first
            calendar = {
            "summary": name,
            "timeZone": "Canada/Saskatchewan" #TO-DO change this to read from the ctx
            }
            created_calender = service.calendars().insert(body=calendar).execute()

            for post in posts:
                # write all the posts as events in the calendar
                start_date = post["duedate"].strftime('%Y-%m-%d')
                end_date = (post["duedate"] + timedelta(days=1)).strftime('%Y-%m-%d')
                print(start_date, end_date)
                event = {
                    'summary': post["class"] + " " + post["name"],
                    'start': {
                        'date': start_date,
                        'timeZone': "Canada/Saskatchewan"
                    },
                    'end': {
                        'date': end_date,
                        'timeZone': "Canada/Saskatchewan"
                    }
                }
                event = service.events().insert(calendarId=created_calender['id'], body=event).execute()
            # get the first event's url as a link to send to the context
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(calendarId=created_calender['id'], timeMin=now,
                                                maxResults=1, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            await ctx.send("Created a new calendar! \n {0}".format(events[0].get('htmlLink')))

def setup(bot):
    b = Calandar(bot)
    bot.add_cog(b)
