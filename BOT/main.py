import discord
import os
import re
import math

client = discord.Client()

db = {"id":("nome","acumulado")}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    keepcharacters = (' ','_', '.', '#')
    nick = "".join(c for c in str(message.author) if c.isalnum() or c in keepcharacters).rstrip()
    id = message.author.id
    if message.author == client.user:
        return

    if message.content.startswith('entregue'):
        value = int(re.search(r'\d+', message.content).group())
        index = message.content.find(str(value))
        offset = math.log(value, 10)
        index += int(offset) + 1
        if len(message.content) > index:
            if message.content[index] == 'k':
                value = value * 1000
        
        if db.get(id):
            previous = db.get(id)[1]
            db[id] = (db[id][0],(previous + value))
        else :
            db[id] = (nick,value)
        await message.channel.send(nick)
        await message.channel.send(value)
        await message.channel.send('Acumulado:')
        valor_sujo = str(db[id][1]) + " em dinheiro sujo"
        await message.channel.send(valor_sujo)
        valor_limpo = "A ser pago: " + str(int(db[id][1]*0.4)) + " em dinheiro limpo"
        await message.channel.send(valor_limpo)


    if message.content.startswith('d@b'):
        await message.channel.send(db)

    if message.content.startswith('lista'):
        for x in db:
            await message.channel.send( str(x) + " : " + str(db[x][0]) + " : " + str(db[x][1]))

    if message.content.startswith('pago'):
        index = message.content.find('@!')
        if index > 0:
            id = int(re.search(r'\d+', message.content).group())
            valor_limpo = db.get(id)[1]
            if valor_limpo:
                db[id] = (db[id][0], 0)
                string = str(int(valor_limpo * 0.4)) + " pago a <@!" + str(id) + ">"
                await message.channel.send(string)
            else:
                await message.channel.send("Não foi possível gravar o pagamento")

        


client.run(os.getenv('BOT_TOKEN'))