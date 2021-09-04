from discord.ext import commands
import sqlite3
import discord
import asyncio
import random



class mobs(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def mob(self,ctx):
		if ctx.channel.id == 717617718177693726:
			mobs1 = ['Кабан','Слизень']
		else:
			await ctx.send('Вы обыскали весь округ, но не нашли ни одного враждебного существа')
			return
		mob = random.choice(mobs1)
		conn = sqlite3.connect(str(ctx.guild.id) +"_база_данных.db") 
		cursor = conn.cursor()
		cursor.execute(f"SELECT id FROM users where id={ctx.author.id}")#все также, существует ли участник в БД
		if cursor.fetchone()==None:
			await ctx.send(f"У <@{ctx.author.id}> не создан персонаж ")
			return

		if mob == 'Слизень':
			Mobhp = 30
			Maxat, Minat = 4,2
		elif mob == 'Кабан':
			Mobhp = 80
			Maxat, Minat = 8,5

			reaction = 'a'
		def check( reaction, user):
			nonlocal msg
			return user == ctx.author and str(reaction.emoji) == '⚔️' or str(reaction.emoji) == '🏃' and str(reaction.message) == str(msg)

		async def reackt(msg):
			nonlocal reaction
			await msg.add_reaction('🏃')
			await msg.add_reaction('⚔️')
			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check = check)
			except asyncio.TimeoutError:
				await ctx.send('Вы бездействуете....')
				return False
			else:
				return True

		async def pat():
			nonlocal Mobhp

			cursor.execute(f"SELECT wid FROM users where id={ctx.author.id}")
			wid = int(str(cursor.fetchone())[1:-2])
			cursor.execute(f"SELECT option FROM items where id={wid}")
			op = str(cursor.fetchone())[2:-3]
			atack = int(op[1:])
			r = random.randint(1,3)
			if op.startswith('w'):
				if r == 3:
					Mobhp = Mobhp - atack * 1.5
					atack = atack * 1.5
				elif r == 2:
					Mobhp = Mobhp - atack


				elif r == 1:
					Mobhp = Mobhp - atack * 0.5
					atack = atack * 0.5

				await ctx.send(f"Вы вмазали ему на {atack} урона! У него осталось {Mobhp} здоровья")
			elif op.startswith('a'):

				cursor.execute(f'SELECT inv FROM users WHERE id = {ctx.author.id}')
				inv = cursor.fetchone()
				inv = str(inv)[3:-4]
				inv = inv.split(', ')
				id = '5'
				atack = atack + 5 
				if id in inv:
					if r == 3:
						Mobhp = Mobhp - atack * 2.0
						atack = atack * 2.0
					elif r == 2:
						Mobhp = Mobhp - atack
					elif r == 1:
						Mobhp = Mobhp - atack * 0.5
						atack = atack *0.5

					inv.remove(id)
					inv = str(inv).replace("'",'')
					cursor.execute(f'UPDATE users SET inv = ? WHERE id = {ctx.author.id}',(inv,))
					await ctx.send(f"Вы попали в него на {atack} урона! У него осталось {Mobhp} здоровья")
				else:
					await ctx.send("У вас нет стрел!")
			elif op.startswith('m'):
				cursor.execute(f'SELECT splv FROM users WHERE id = {ctx.author.id}')
				splv = int(str(cursor.fetchone())[3:-10])
				cursor.execute(f'SELECT mp FROM users WHERE id = {ctx.author.id}')
				mana = int(str(cursor.fetchone())[1:-2])
				if splv == 1:
					sps = random.randint(3,7) + atack
					mp = 20
					nam = 'Искрой'
				if mana >= mp:
					Mobhp = Mobhp - sps
					await ctx.send(f"Вы зарядили в него {nam} и нанесли {sps} урона.  У него осталось {Mobhp} здоровья")
					cursor.execute(f'UPDATE users SET mp = {mana - mp} WHERE id = {ctx.author.id}')
				else:
					await ctx.send('У вас не хватает маны!')

		async def mobdead():
			nonlocal Mobhp, mob
			if Mobhp <= 0:
				if mob == 'Cлизень':
					if  random.randint(1,10) < 8:
						mon = random.randint(20,35)
						cursor.execute(f"SELECT money FROM users where id={ctx.author.id}")
						money = float(str(cursor.fetchone())[1:-2]) + mon
						await ctx.send(f'Тебе выпало {mon} монет\nУ тебя сейчас {money} монет')
						return
					else:
						await ctx.send(f'Тебе не повезло, ничего не выпало :<  ')
						return
				elif mob == 'Кабан':
					r = random.randint(1,3)
					if r == 1:
						mon = random.randint(40,50)
						cursor.execute(f"SELECT money FROM users where id={ctx.author.id}")
						money = float(str(cursor.fetchone())[1:-2]) + mon
						await ctx.send(f'Тебе выпало {mon} монет\nУ тебя сейчас {money} монет')
						return   
					elif r == 2:
						count = random.randint(1,3)
						cursor.execute(f'SELECT inv FROM users WHERE id = {ctx.author.id}')
						inv = str(cursor.fetchone())[3:-4]
						if inv == '':
							inv = []
						else:
							inv = inv.split(',')
						a=0
						while a < count:
							inv.append(6)
							a += 1
						now_inv = []
						for i in inv:
							i = int(i)
							now_inv.append(i)
						inv = str(now_inv)
						cursor.execute(f'UPDATE users SET inv = ? WHERE id = {ctx.author.id}',(inv,))
						await ctx.send(f'Тебе выпало {count} кожи')
						return
					elif r == 3:
						count = random.randint(1,3)
						cursor.execute(f'SELECT inv FROM users WHERE id = {ctx.author.id}')
						inv = str(cursor.fetchone())[3:-4]
						if inv == '':
							inv = []
						else:
							inv = inv.split(',')
						a=0
						while a < count:
							inv.append(7)
							a += 1
						now_inv = []
						for i in inv:
							i = int(i)
							now_inv.append(i)
						inv = str(now_inv)
						cursor.execute(f'UPDATE users SET inv = ? WHERE id = {ctx.author.id}',(inv,))
						await ctx.send(f'Тебе выпало {count} сырого мяса ')
						return
			else:
				return 'i'

		msg = await ctx.send(f'На тебя напал {mob}!')
		if await reackt(msg)== True:
			if str(reaction.emoji) == '⚔️':
				await pat()
				conn.commit()
			elif str(reaction.emoji) == '🏃':
				await ctx.send('Вы сбежали')
				return
				conn.commit()
			if await mobdead() != 'i':
				return
				conn.commit()
		while Mobhp > 0:
			cursor.execute(f"SELECT armor FROM users where id={ctx.author.id}")
			arm  = float(str(cursor.fetchone())[1:-2])
			if arm > 0:
				hp = arm
				whatisit = 'брони'
				wii = "armor"
			else:
				cursor.execute(f"SELECT hp FROM users where id={ctx.author.id}")
				hp  = float(str(cursor.fetchone())[1:-2])
				whatisit = 'здоровья'
				wii = 'hp'
			mat = random.randint(Minat,Maxat)
			hp = hp - mat
			cursor.execute(f'UPDATE users SET {wii} = {hp} WHERE id = {ctx.author.id}')
			msg = await ctx.send(f"{mob} Атакует! Он нанес тебе {mat} урона. У тебя осталось {hp} {whatisit} ")
			conn.commit()
			if await reackt(msg)== True:

				if str(reaction.emoji) == '⚔️':
					await pat()
					conn.commit()
				elif str(reaction.emoji) == '🏃':
					await ctx.send('Вы сбежали')
					return
					conn.commit()
		if await mobdead() != 'i':
			return
			conn.commit()


		conn.commit()
		conn.close()

		
		

def setup(bot):
	bot.add_cog(mobs(bot))