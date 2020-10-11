# duedatebot
a due date reminder bot for discord 
Create new Due-Dates, sort them by Course, and add what files you need to hand in! 

## Contributing: 
### Dependancies:
You will need to install the following packages via pip:
 - discord
 - pymongo
 - dotenv
 
 ### Setting up the Environment
 After making sure you have the proper python packages, clone the repo. In the same directory as the codebase, create a file called .env, with the following content:
 ```
 # .env
DISCORD_TOKEN=<Your discord bot token>
DB_PASS=<Your mongodb token>
 ```
For developing, you should create your own discord bot and test server to run it in. Once anything is merged with main, it will be pushed to Heroku and built, and will then use the Live bots tokens. 

For the database, you have 2 options. If you are worried about messing up the existing live database, you can create your own cluster with MongoDB. At this stage, you can use the current database, its unlikely you will mass delete anything important since its only live on 1 server while we develop. Message duckypotato on discord if you want the token. 
 
 ### What to do? 

 - Writing Documentation (ESPECIALLY doctstrings)
 - Screenshots of commands in action (so we can put them on this page!)
 - Writing better help messages
 - Writing more interesting reply messaages
 - Coming up with ideas for commands 
 - Adding command Aliases
 
Check out Issues for stuff you can help out with!
