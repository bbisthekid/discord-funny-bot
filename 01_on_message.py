import discord
from discord.ext import commands
from decouple import config
import re
import sqlite3
import hashlib
import datetime

DISCORD_TOKEN = config('TOKEN')

patterns = ['er', 'eR', 'Er', 'ER']

client = commands.Bot(command_prefix='!!')

# check if database is made and load it
db = sqlite3.connect('quotebot_db.sqlite')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS quotes (id TEXT primary key, user VARCHAR, quoteMessage VARCHAR, date TEXT)')
print("Loaded Database")

db.commit()


# initialize the bot
@client.event
async def on_ready():
    print('Connected to discord as {0.user}'.format(client))


# commands #

# test command
@client.command()
async def echo(ctx, *, user_message):
    await ctx.send('User said: ' + user_message)


# help menu
@client.command()
async def quotehelp(ctx):
    embed = discord.Embed(name="help")
    embed.set_author(name="Quotebot commands:")
    embed.add_field(name="To quote:", value="!quote @[user] [message]", inline=False)
    embed.add_field(name="To display", value="!getquote @[user]", inline=False)
    embed.add_field(name="Random quote from a random user", value="!random", inline=False)
    await ctx.send(embed=embed)


# print random quote
@client.command()
async def random(ctx):
    cursor.execute("SELECT user, quoteMessage,date FROM quotes ORDER BY RANDOM() LIMIT 1")
    query = cursor.fetchone()

    # log
    print(query[0]+": \""+query[1]+"\" printed to the screen "+str(query[2]))

    # embeds the output
    style = discord.Embed(name="responding quote", description="- "+str(query[0])+" "+str(query[2]))
    style.set_author(name=str(query[1]))
    await ctx.send(embed=style)


# create a quote
@client.command()
async def quote(ctx, *, message: str):

    # split the message into words
    string = str(message)
    temp = string.split()

    # take the username out
    user = temp[0]
    del temp[0]

    # join the message back together
    text = " ".join(temp)

    if user[0] != '@':
        await ctx.send("Use ```@[user] [message]``` to quote a person")
        return

    uniqeuid = hash(user+message)

    # date and time of the message
    time = datetime.datetime.now()
    formatted_time = str(time.strftime("%d-%m-%Y %H:%M"))

    # find if message is in the db already
    cursor.execute("SELECT count(*) FROM quotes WHERE id = ?", (uniqeuid,))
    find = cursor.fetchone()[0]

    if find > 0:
        return

    # insert into database
    cursor.execute("INSERT INTO quotes VALUES(?,?,?,?)", (uniqeuid, user, text, formatted_time))
    await ctx.send("Quote successfully added")

    db.commit()

    # number of words in the database
    rows = cursor.execute("SELECT * from quotes")

    # log to terminal
    print(str(len(rows.fetchall()))+". added - "+str(user)+": \""+str(text)+"\" to database at "+formatted_time)


@client.command()
async def getquote(ctx, message: str):

    # sanitize name
    user = (message,)

    try:
        cursor.execute("SELECT quoteMessage,date FROM quotes WHERE user=(?) ORDER BY RANDOM() LIMIT 1", user)
        query = cursor.fetchone()

        # adds quotes to message
        output = "\""+str(query[0])+"\""

        # log
        print(message+": \""+output+"\" printed to the screen "+str(query[1]))

        # embeds the output to make it pretty
        style = discord.Embed(name="responding quote", description="- "+message+" "+str(query[1]))
        style.set_author(name=output)
        await ctx.send(embed=style)

    except Exception:

        await ctx.send("No quotes of that user found")

    db.commit()

# # hardly know her function
# @client.event
# async def on_message(message):
#     # check if the bot sent the message to avoid an infinite loop
#     if message.author == client.user:
#         return
#     # check within the predetermined patterns array for word that end in er
#     for pattern in patterns:
#         if re.search(pattern, message.content):
#             response = re.findall(rf'\b\w+{re.escape(pattern)}\b', message.content, re.MULTILINE)
#             new_response = response[0].lower().capitalize()
#             await message.channel.send(new_response + "? I hardly know 'er.")


# hardly know her function
@client.listen('on_message')
async def hardly_know_her(message):
    # check if the bot sent the message to avoid an infinite loop
    if message.author == client.user:
        return
    # check within the predetermined patterns array for word that end in er
    for pattern in patterns:
        if re.search(pattern, message.content):
            response = re.findall(rf'\b\w+{re.escape(pattern)}\b', message.content, re.MULTILINE)
            new_response = response[0].lower().capitalize()
            await message.channel.send(new_response + "? I hardly know 'er.")


client.run(DISCORD_TOKEN)
