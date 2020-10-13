"""
Helper functions for the bot
"""
from datetime import datetime

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
