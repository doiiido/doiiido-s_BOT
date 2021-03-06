import discord
import os
import re
import math
import mysql.connector

client = discord.Client()

porcentagem = 0.4

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):    
	#print(message.guild)
	#print(message.channel.category)
	#print(message.channel)
	#print(message.channel.id)
	#print(message.author)
	#print(message.author.display_name)
	#print(message.author.name)
	#print(message.author.nick)
	#print(message.author.id)
	mydb = mysql.connector.connect(host="192.168.21.11",user="root",password="toor",database='BOT' )
	cursor = mydb.cursor(named_tuple=True)

	keepcharacters = (' ','_', '.', '#')
	nick = "".join(c for c in str(message.author.display_name) if c.isalnum() or c in keepcharacters).rstrip()
	user_id = message.author.id
	channel_id = message.channel.id
	if message.author == client.user:
		return

	#Hardcoding developer's ID
	if user_id == 451507492199989258:
		if message.content.startswith('!d@b'):
			cursor.execute("SELECT * FROM tbl_channels")
			channels = cursor.fetchall()
			await message.channel.send(channels)
			cursor.execute("SELECT * FROM tbl_users")
			users = cursor.fetchall()
			await message.channel.send(users)

	cursor.execute("SELECT * FROM tbl_channels WHERE id = %s", (channel_id, ))
	channel = cursor.fetchone()
	if not(channel):
		if user_id == 451507492199989258:
			if message.content.startswith('!Start_BOT'):
				index = message.content.find('@!')
				if index > 0:
					user_id = int(re.search(r'\d+', message.content).group())
					if user_id == client.user.id:
						guild = "".join(c for c in str(message.guild) if c.isalnum() or c in keepcharacters).rstrip()
						category = "".join(c for c in str(message.channel.category) if c.isalnum() or c in keepcharacters).rstrip()
						name = "".join(c for c in str(message.channel) if c.isalnum() or c in keepcharacters).rstrip()
						cursor.execute("INSERT INTO tbl_channels(id, guild, category, name) VALUES(%s, %s, %s, %s)", (channel_id, guild, category, name))
						mydb.commit()
						await message.channel.send('Canal Autorizado')
	else:
		if message.content.startswith('!entregue'):
			value = int(re.search(r'\d+', message.content).group())
			index = message.content.find(str(value))
			offset = math.log(value, 10)
			index += int(offset) + 1
			if len(message.content) > index:
				if message.content[index] == 'k':
					value = value * 1000

			cursor.execute("SELECT * FROM tbl_channels WHERE id = %s", (channel_id, ))
			channel = cursor.fetchone()
			if not(channel):
				cursor.close()
				mydb.close()
				return
			if user_id == 451507492199989258:
				index = message.content.find('@!')
				if index > 0:
					user_id = int(re.search(r'\d+', message.content[index:]).group())
				index = message.content.find('|!') + 2
				if index > 0:
					nick = str(message.content[index:])
			cursor.execute("SELECT * FROM tbl_users WHERE channel_id = %s AND user_id = %s", (channel_id, user_id))
			user = cursor.fetchone()
			if user:
				previous = int(user.valor_sujo)
				previous += value
				cursor.execute("UPDATE tbl_users SET valor_sujo=%s WHERE channel_id=%s AND user_id=%s", (previous, channel_id, user_id))
				mydb.commit()
			else :
				cursor.execute("INSERT INTO tbl_users(user_id, channel_id, nick, valor_sujo) VALUES(%s, %s, %s, %s)", (user_id, channel_id, nick, value))
				mydb.commit()
			
			cursor.execute("SELECT * FROM tbl_users WHERE channel_id = %s AND user_id = %s", (channel_id, user_id))
			user = cursor.fetchone()
			await message.channel.send(nick)
			await message.channel.send(value)
			await message.channel.send('Acumulado:')
			valor_sujo = str(user.valor_sujo) + " em dinheiro sujo"
			await message.channel.send(valor_sujo)
			valor_limpo = "A ser pago: " + str(int(int(user.valor_sujo)*porcentagem)) + " em dinheiro limpo"
			await message.channel.send(valor_limpo)

		if message.content.startswith('!lista'):
			cursor.execute("SELECT * FROM tbl_users WHERE channel_id = %s", (channel_id, ))
			user = cursor.fetchall()
			if user:
				at_least_one = 0
				for x in user:
					if int(x.valor_sujo) > 0:
						at_least_one = 1
						buff = "_ \n" 
						buff += x.nick + '\n'
						buff += 'Acumulado: '+str(x.valor_sujo) + " em dinheiro sujo\n" 
						buff += "A ser pago: " + str(int(int(x.valor_sujo)*porcentagem)) + " em dinheiro limpo \n"
						await message.channel.send(buff)
				if at_least_one == 0:
					await message.channel.send("N??o h?? pagamentos pendentes")

			else: 
				await message.channel.send("N??o h?? pagamentos pendentes")

		if message.content.startswith('!pago'):
			index = message.content.find('@!')
			if index > 0:
				user_id = int(re.search(r'\d+', message.content).group())
				cursor.execute("SELECT * FROM tbl_users WHERE channel_id = %s AND user_id = %s", (channel_id, user_id))
				user = cursor.fetchone()
			if int(user.valor_sujo) != 0:
				string = str(int(int(user.valor_sujo) * 0.4)) + " pago a <@!" + str(user_id) + ">"
				cursor.execute("UPDATE tbl_users SET valor_sujo=%s WHERE channel_id=%s AND user_id=%s", (0, channel_id, user_id))
				mydb.commit()
				await message.channel.send(string)
			else:
				await message.channel.send("N??o h?? pagamento pendente para esta pessoa")

		
		cursor.close()
		mydb.close()


client.run(os.getenv('BOT_TOKEN'))