import discord
import os
import re
import math

client = discord.Client()

db = {"nome":"acumulado"}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    keepcharacters = (' ','_')
    nick = "".join(c for c in str(message.author) if c.isalnum() or c in keepcharacters).rstrip()
    if message.author == client.user:
        return

    if message.content.startswith('bot'):
        value = int(re.search(r'\d+', message.content).group())
        index = message.content.find(str(value))
        offset = math.log(value, 10)
        index += int(offset) + 1
        if message.content[index] == 'k':
            value = value * 1000
        previous = db.get(nick)
        if previous:
            db[nick] = previous + value
        else :
            db[nick] = value
        await message.channel.send(nick)
        await message.channel.send(value)
        await message.channel.send('Acumulado:')
        await message.channel.send(db[nick])

    if message.content.startswith('list'):
        
        await message.channel.send(db)
        


client.run(os.getenv('BOT_TOKEN'))