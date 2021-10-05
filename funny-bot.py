import discord
from discord.ext import commands
from decouple import config
import re
import sqlite3
import time
import datetime

DISCORD_TOKEN = config('TOKEN')

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


# -------commands---------- #

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
async def quote(ctx, user: str, message: str):

    # # split the message into words
    # string = str(message)
    # temp = string.split()

    # # take the username out
    # user = temp[0]
    # del temp[0]

    # # join the message back together
    # # text = " ".join(temp)

    if not message:
        await ctx.send("Use ```@[user] [message]``` to quote a person")
        return

    if not re.search('@', message):
        await ctx.send("Use ```@[user] [message]``` to quote a person")
        return

    

    user = user.replace("<","")
    user = user.replace(">","")
    user = user.replace("@","")
    user = user.replace("!","")

    uniqeuid = hash(user+message)

    # date and time of the message
    message_time = datetime.datetime.now()
    formatted_time = str(message_time.strftime("%d-%m-%Y %H:%M"))

    # find if message is in the db already
    cursor.execute("SELECT count(*) FROM quotes WHERE id = ?", (uniqeuid,))
    find = cursor.fetchone()[0]

    if find > 0:
        return

    # insert into database
    cursor.execute("INSERT INTO quotes VALUES(?,?,?,?)", (uniqeuid, user, message, formatted_time))
    await ctx.send("Quote successfully added")

    db.commit()

    # number of words in the database
    rows = cursor.execute("SELECT * from quotes")

    # log to terminal
    print(str(len(rows.fetchall()))+". added - "+str(user)+": \""+str(message)+"\" to database at "+formatted_time)


@client.command()
async def getquote(ctx, message: str):
    if not re.search('@', message):
        await ctx.send("Use ```@[user] [message]``` to quote a person")
        return

    user = message
    message = message.replace("<","")
    message = message.replace(">","")
    message = message.replace("@","")
    message = message.replace("!","")
    print(message)

    # # sanitize name
    # user = (message,)

    try:
        sql = "SELECT quoteMessage, date FROM quotes WHERE user =" + "'" + message + "'" + " ORDER BY RANDOM() LIMIT 1"
        print(sql)
        # cursor.execute("SELECT quoteMessage,date FROM quotes WHERE user=(?) ORDER BY RANDOM() LIMIT 1", message)
        cursor.execute(sql)
        query = cursor.fetchone()

        # adds quotes to message
        output = "\""+str(query[0])+"\""

        # log
        print(message+": \""+output+"\" printed to the screen "+str(query[1]))

        # embeds the output to make it pretty
        style = discord.Embed(name="responding quote", description="- "+user+" "+str(query[1]))
        style.set_author(name=output)
        await ctx.send(embed=style)

    except Exception:

        await ctx.send("No quotes of that user found")

    db.commit()


# join and say a peter quote in voice then leave
@client.command()
async def peterquote(ctx):
    voice_channel = ctx.author.voice.channel
    # channel = None
    if voice_channel is not None:
        # channel = voice_channel.name
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable="C:/FFmpeg/ffmpeg.exe", source="sounds/peter-hurt.mp3"))
        # sleep while the audio is playing():
        while vc.is_playing():
            time.sleep(1)
        await vc.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")
    # delete the command after the audio is done playing
    # await ctx.message.delete()


# hardly know her function
@client.listen('on_message')
async def hardly_know_her(message):
    # check if the bot sent the message to avoid an infinite loop
    if message.author == client.user:
        return
    # check if the message is a spoiler text
    # spoiler_text = re.findall(rf'\b||\w+||\b', message.content, re.MULTILINE)
    if re.search(re.escape("||"), message.content) is not None:
        return
    # check for word that end in er
    # print(message.content)
    if re.search('er', message.content.lower()):
        if re.findall(rf'\ber\b', message.content, re.MULTILINE):
            await message.channel.send("Hardly know 'er.")
            return
        response = re.findall(rf'\b\w+er\b', message.content, re.MULTILINE)
        if response:
            new_response = response[0].lower().capitalize()
            await message.channel.send(new_response + "? I hardly know 'er.")
            return
    # check if message is balls
    if re.search('balls', message.content.lower()):
        await message.channel.send("haha")
        return
    # check if message is mike
    if re.search('mike', message.content.lower()):
        await message.channel.send("Mike Balls gotten")
        return


client.run(DISCORD_TOKEN)
