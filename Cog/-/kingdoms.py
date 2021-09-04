import discord
from discord.ext import commands
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io
import sys
import random
from random import choice
import asyncio
import nekos
import time
import os
from Cybernator import Paginator
import pymongo
from bs4 import BeautifulSoup as BS
from collections import Counter


client2 = pymongo.MongoClient("mongodb+srv://host:1394@cluster0.rkh6o.mongodb.net/<dbname>?retryWrites=true&w=majority")
rpg = client2.bot

auc = rpg.auc
bback = rpg.backs
items = rpg.items
players = rpg.players
regions = rpg.regions
kingdoms = rpg.kingdoms


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def ship_create(self, ctx, *, name = None):

        if name is None:
            emb = discord.Embed(description = 'Введите название королевства!',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
            await ctx.send(embed = emb)

        elif len(name) > 25:
            emb = discord.Embed(description = 'Имя королевства слишком длиное!',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
            await ctx.send(embed = emb)

        else:
            player = players.find_one({"userid": ctx.author.id})
            balance = player['money']
            if balance < 10000:
                emb = discord.Embed(description = 'Недостаточно монет!',color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                await ctx.send(embed = emb)

            else:
                if kingdoms.count_documents({"name": name}):
                    emb = discord.Embed(description = 'Такое королевство уже существует!',color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                    await ctx.send(embed = emb)
                else:
                    ship = player['kingship']
                    if ship != 777777777777777777:
                        emb = discord.Embed(description = f'Вы уже в королестве',color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                        await ctx.send(embed = emb)
                    else:
                        emb = discord.Embed(description = 'Вы успешно создали королевство!',color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                        await ctx.send(embed = emb)
                        kingdoms.insert_one({"owner": ctx.author.id, "name": name, "bio": 'Пусто', "flag": None, "cash": 0, "created": time.strftime('%X, %d %B, %Y'), "members": [ctx.author.id]})
                        m = balance - 10000
                        players.update_one({"userid": ctx.author.id}, {"$set": {"money": m}}) 
                        players.update_one({"userid": ctx.author.id}, {"$set": {"kingship": ctx.author.id}}) 




    @commands.command()
    async def ship_info(self, ctx, *, name = None):
        dom = kingdoms.find_one({"name": name})
        data = dom['created']
        members = dom['members']

        if name is None:
            emb = discord.Embed(description = 'Введите название клана!',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
            await ctx.send(embed = emb)

        else:
            try:
                if kingdoms.count_documents({"name": name}):
                    for dom in kingdoms.find({"name": name}):

                        text = " "

                        emb1 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_thumbnail(url = dom["flag"]).set_author(icon_url = '{}'.format(dom["flag"]), name = f'Kingdom info | {name}')
                        emb2 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_thumbnail(url = dom["flag"]).set_author(icon_url = '{}'.format(dom["flag"]), name = f'Kingdom info | {name}')
                        emb3 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_thumbnail(url = dom["flag"]).set_author(icon_url = '{}'.format(dom["flag"]), name = f'Kingdom info | {name}')


                        embeds = [emb1,emb2,emb3]
                        embs=[]
                        c = 3
                        n = []
                        for i in members:
                            if not i in n:
                                user = players.find_one({"userid": int(i)})
                                text = text + f"<@{user['userid']}>\n"
                                n.append(i)
                            if c == 3:
                                c = 0
                                a += 1
                                embs.append(embeds[a])
                            c += 1

                        msg = await ctx.send(embed = embs[0])
                        if len(embs) > 1:
                            page = Paginator(self.bot, msg, only=ctx.author, footer=False, embeds=embs)
                            await page.start()



                else:
                    emb = discord.Embed(description = 'Такого клана не существует!',color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                    await ctx.send(embed = emb)

            except:
                if kingdoms.count_documents({"name": name}):
                    for dom in kingdoms.find({"name": name}):

                        text = " "

                        emb1 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_author(name = f'Kingdom info | {name}')

                        emb2 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_author(name = f'Kingdom info | {name}')

                        emb3 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                        ).add_field(name = 'Казна клана:', value = f'{dom["cash"]}').add_field(name = 'Владелец:', value = f'{self.bot.get_user(dom["owner"])}'
                        ).add_field(name = 'Дата создания:', value = f'{data}', inline = False).add_field(name = 'Участники:', value = f'{text}'
                        ).set_author(name = f'Kingdom info | {name}')


                        embeds = [emb1,emb2,emb3]
                        embs=[]
                        a = -1
                        c = 3
                        n = []
                        for i in members:
                            if not i in n:
                                user = players.find_one({"userid": int(i)})
                                text = text + f"<@{user['userid']}>\n"
                                n.append(i)
                            if c == 3:
                                c = 0
                                a += 1
                                embs.append(embeds[a])
                            c += 1

                        msg = await ctx.send(embed = embs[0])
                        if len(embs) > 1:
                            page = Paginator(self.bot, msg, only=ctx.author, footer=False, embeds=embs)
                            await page.start()

                else:
                    emb = discord.Embed(description = 'Такого клана не существует!',color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                    await ctx.send(embed = emb)

	# @clan.command()
	# async def banner(self, ctx, link = None):

	# 		if link is None:
	# 			emb = discord.Embed(description = 'Укажите ссылку на баннер для клана!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:				
	# 			try:
	# 				if clan.count_documents({"owner": ctx.author.id}):
	# 					balance = db['test']

	# 					if balance.find_one({"_id": ctx.author.id})['cash'] > 5000:
								
	# 						emb = discord.Embed(description = 'Вы поменяли баннер клана!', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))

	# 						emb.set_image(url = link)

	# 						await ctx.send(embed = emb)
	# 						await ctx.message.delete()

	# 						name = clan.find_one({"owner": ctx.author.id})['name']
								
	# 						clan.update_one({"name": name}, {"$set": {"flag": link}}) 

	# 						newcash = balance.find_one({"_id": ctx.author.id})['cash'] - 5000
	# 						balance.update_one({"_id": ctx.author.id}, {"$set": {"cash": newcash}}) 
							
	# 					else:
								
	# 						emb = discord.Embed(description = 'Недостаточно денег!', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 						await ctx.send(embed = emb)
	# 				else:
	# 					emb = discord.Embed(description = 'Только глава может поменять баннер клана!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)

	# 					await ctx.message.delete()		
	# 			except:
	# 				emb = discord.Embed(description = 'Уажите ссылку на картинку!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 				await ctx.message.delete()	

	# @clan.command()
	# async def bio(self, ctx, *, bio = None):
	# 	if ctx.channel.id != 777:	
	# 		if clan.count_documents({"owner": ctx.author.id}):

	# 			if bio is None:
	# 				emb = discord.Embed(description = 'Укажите описание!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			elif len(bio) > 120:
	# 				emb = discord.Embed(description = 'Слишком много символов(макс: 120)', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))

	# 				await ctx.send(embed = emb)

	# 			else:

	# 				emb = discord.Embed(description = f'Вы поменяли описание вашего клана на:\n```fix\n{bio}```', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 				name = clan.find_one({"owner": ctx.author.id})['name']

	# 				clan.update_one({"name": name}, {"$set": {"bio": bio}}) 
			
	# 		else:
	# 			emb = discord.Embed(description = 'Только глава может поменять описание клана!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def invite(self, ctx, member: discord.Member = None):
	# 	if ctx.channel.id == 777:

	# 		if member is None:
	# 			emb = discord.Embed(description = 'Укажите пользователя!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:
	# 			if clan.count_documents({"owner": ctx.author.id}):
	# 				name = clan.find_one({"owner": ctx.author.id})['name']

	# 				if not clan2.count_documents({"_id": member.id}):
							
	# 					solutions = ['✅', '❌']
	# 					emb = discord.Embed(title = f'Кланы {ctx.guild.name}', description = f'**{member}** хотите ли вы вступить в клан **{name}?**', timestamp = datetime.datetime.utcnow())
							
	# 					message = await ctx.send(embed = emb)
							
	# 					for x in solutions:
	# 						await message.add_reaction(x)

	# 					try:
	# 						react, user = await self.Bot.wait_for('reaction_add', timeout= 30.0, check= lambda react, user: user == member and react.message.channel == ctx.channel and react.emoji in solutions)
	# 					except asyncio.TimeoutError:
	# 						emb = discord.Embed(description = 'Время на ответ вышло', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))

	# 						await message.edit(embed = emb)
	# 						await message.clear_reactions()
	# 					else:
	# 						if str(react.emoji) == '✅':
	# 							await message.clear_reactions()

	# 							emb = discord.Embed(title = f'Кланы {ctx.guild.name}', description = f'**{member}** вступил в клан **{name}!**', timestamp = datetime.datetime.utcnow())
	# 							await message.edit(embed = emb)
								
	# 							clan2.insert_one({"_id": member.id, "name": name, "clanid": ctx.author.id})

	# 							for x in clan.find({"name": name}):
	# 								members = x['members'] + 1
									
	# 								clan.update_one({"name": name}, {"$set": {"members": members}}) 
									
	# 						elif str(react.emoji) == '❌':
	# 							await message.clear_reactions()

	# 							emb = discord.Embed(title = f'Кланы {ctx.guild.name}', description = f'**{member}** отказался от приглашения!', timestamp = datetime.datetime.utcnow())

	# 							await message.edit(embed = emb)

	# 				else:

	# 					emb = discord.Embed(description = 'Пользователь уже в клане!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
	# 					await ctx.send(embed = emb)
	# 			else:

	# 				emb = discord.Embed(description = 'Только глава может приглашать людей!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
	# 				await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def owner(self, ctx, member: discord.Member = None):
	# 	if ctx.channel.id != 777:

	# 		if member is None:
	# 			emb = discord.Embed(description = 'Укажите пользователя!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:

	# 			if not clan2.count_documents({"_id": ctx.author.id}):
	# 				emb = discord.Embed(description = 'Вы не в клане!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			elif not clan2.count_documents({"_id": member.id}):
	# 				emb = discord.Embed(description = 'Пользователь не в клане!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)


	# 			elif not clan.count_documents({"owner": ctx.author.id}):
	# 				emb = discord.Embed(description = 'Только глава может отдать владельца клана!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			else:
	# 				clanName = clan2.find_one({"_id": ctx.author.id})['name']
	# 				clanNameTwo = clan2.find_one({"_id": member.id})['name']

	# 				if clanName == clanNameTwo:
	# 					emb = discord.Embed(description = f'Вы успешно передали лидерство **{member}**', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)

	# 					clan.update_one({"name": clanName}, {"$set": {"owner": member.id}}) 

	# 					clan2.update_one({"name": clanName}, {"$set": {"clanid": member.id}}) 

	# 				else:
	# 					emb = discord.Embed(description = 'Пользователь в другом клане!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def top(self, ctx, name = None):
	# 	if ctx.channel.id != 777:
	# 		if name is None:
	# 			emb = discord.Embed(description = 'Существующие топы: <member> <cash>', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
	# 			await ctx.send(embed = emb)

	# 		else:
	# 			if name.lower() == 'member':

	# 				emb = discord.Embed(description = f':trophy: **[Топ 10 кланов по участникам:]({ctx.author.avatar_url})**')

	# 				counter = 0
	# 				for j in clan.find({"$query":{}, "$orderby":{"members":-1}}).limit(10):
	# 					counter += 1

	# 					if counter == 1:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :first_place: # {j["name"]}',
	# 							value = f'| Участников: {j["members"]}',
	# 							inline = False
	# 						)
	# 					elif counter == 2:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :second_place: # {j["name"]}',
	# 							value = f'| Участников: {j["members"]}',
	# 							inline = False
	# 						)
	# 					elif counter == 3:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :third_place: # {j["name"]}',
	# 							value = f'| Участников: {j["members"]}',
	# 							inline = False
	# 						)
	# 					else:

	# 						emb.add_field(
	# 							name = f'[{counter}]    > # {row[1]}',
	# 							value = f'| Участников: {j["members"]}',
	# 							inline = False
	# 						)
	# 				emb.set_author(name = f'Страница 1 из 1 — Всего учатников: {len(ctx.guild.members)}', icon_url = '{}'.format(ctx.guild.icon_url))
	# 				await ctx.send(embed = emb)

	# 			elif name.lower() == 'cash':
	# 				emb = discord.Embed(description = f':trophy: **[Топ 10 кланов по балансу:]({ctx.author.avatar_url})**')

	# 				counter = 0
	# 				for j in clan.find({"$query":{}, "$orderby":{"cash":-1}}).limit(10):
	# 					counter += 1

	# 					if counter == 1:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :first_place: # {j["name"]}',
	# 							value = f'| Баланс: <a:currency:737351940320657588> {j["cash"]}',
	# 							inline = False
	# 						)
	# 					elif counter == 2:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :second_place: # {j["name"]}',
	# 							value = f'| Баланс: <a:currency:737351940320657588> {j["cash"]}',
	# 							inline = False
	# 						)
	# 					elif counter == 3:
	# 						emb.add_field(
	# 							name = f'[{counter}]    > :third_place: # {j["name"]}',
	# 							value = f'| Баланс: <a:currency:737351940320657588> {j["cash"]}',
	# 							inline = False
	# 						)
	# 					else:

	# 						emb.add_field(
	# 							name = f'[{counter}]    > # {j["name"]}',
	# 							value = f'| Баланс: <a:currency:737351940320657588> {j["cash"]}',
	# 							inline = False
	# 						)
	# 				emb.set_author(name = f'Страница 1 из 1 — Всего учатников: {len(ctx.guild.members)}', icon_url = '{}'.format(ctx.guild.icon_url))
	# 				await ctx.send(embed = emb)
	# 			else:
	# 				emb = discord.Embed(description = 'Существующие топы: <member> <cash>', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
	# 				await ctx.send(embed = emb)
		
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def leave(self, ctx):
	# 	if ctx.channel.id != 777:

	# 		if clan2.find_one({"_id": ctx.author.id})['name'] is None:
				
	# 			emb = discord.Embed(description = 'Вы не в клане!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:

	# 			if not clan.count_documents({"owner": ctx.author.id}):
	# 				name = clan2.find_one({"_id": ctx.author.id})['name']

	# 				emb = discord.Embed(description = f'Вы покинули клан {name}!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 				clan2.delete_one({"_id": ctx.author.id})

	# 				for x in clan.find({"name": name}):
	# 					members = x['members'] - 1
									
	# 					clan.update_one({"name": name}, {"$set": {"members": members}}) 
			
	# 			else:
	# 				emb = discord.Embed(description = 'Глава не может покинуть клан!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def kick(self, ctx, member: discord.Member = None):
	# 	if ctx.channel.id != 777:

	# 		if member is None:
	# 			emb = discord.Embed(description = 'Укажите пользователя', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		elif member == ctx.author:
	# 			emb = discord.Embed(description = 'Самого себя кикнуть нельзя!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:

	# 			if not clan2.count_documents({"_id": ctx.author.id}):
					
	# 				emb = discord.Embed(description = 'Вы не в клане!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			elif not clan2.count_documents({"_id": member.id}):
					
	# 				emb = discord.Embed(description = 'Пользователь не в клане!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			else:
	# 				if not clan.count_documents({"owner": ctx.author.id}):

	# 					emb = discord.Embed(description = 'Только глава может кикнуть участника с клана!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)

	# 				else:
	# 					clanName1 = clan2.find_one({"_id": ctx.author.id})['name']
	# 					clanName2 = clan2.find_one({"_id": member.id})['name']

	# 					if clanName1 == clanName2:
	# 						emb = discord.Embed(description = 'Вы успешно кикнули участника с клана!', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 						await ctx.send(embed = emb)

	# 						name = clan2.find_one({"_id": ctx.author.id})['name']
							
	# 						clan2.delete_one({"_id": member.id})

	# 						for x in clan.find({"name": name}):
	# 							members = x['members'] - 1
									
	# 							clan.update_one({"name": name}, {"$set": {"members": members}}) 

	# 					else:
	# 						emb = discord.Embed(description = 'Данный человек находится в другом клане!', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 						await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def delete(self, ctx):
	# 	if ctx.channel.id != 777:

	# 		if not clan2.count_documents({"_id": ctx.author.id}):
					
	# 			emb = discord.Embed(description = 'Вы не в клане!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:
	# 			if not clan.count_documents({"owner": ctx.author.id}):

	# 				emb = discord.Embed(description = 'Только глава может удалить клан!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			else:
	# 				emb = discord.Embed(description = 'Вы успешно удалили клан!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 				name = clan2.find_one({"_id": ctx.author.id})['name']

	# 				clan.delete_one({"name": name})

	# 				for x in clan2.find({"name": name}):
	# 					clan2.delete_one({"name": name})
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def award(self, ctx, amount: int = None):
	# 	if ctx.channel.id != 777:

	# 		if amount is None:
	# 			emb = discord.Embed(description = 'Укажите сумму!')
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		elif amount < 30:
	# 			emb = discord.Embed(description = 'Сумма слишком маленькая!')
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:
	# 			if not clan2.count_documents({"_id": ctx.author.id}):
	# 				emb = discord.Embed(description = 'Вы не в клане!')
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			else:

	# 				balance = db['test']

	# 				if balance.find_one({"_id": ctx.author.id})['cash'] < amount:
	# 					emb = discord.Embed(description = 'Сумма перевода больше суммы баланса!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)
	# 				else:

	# 					emb = discord.Embed(description = f'Вы успешно перевели в казну клана <a:currency:737351940320657588> {amount}', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)

	# 					name = clan2.find_one({"_id": ctx.author.id})['name']
											
	# 					newcash1 = clan.find_one({"name": name})['cash'] + amount
	# 					clan.update_one({"name": name}, {"$set": {"cash": newcash1}}) 
				
	# 					newcash2 = balance.find_one({"_id": ctx.author.id})['cash'] - amount
	# 					balance.update_one({"_id": ctx.author.id}, {"$set": {"cash": newcash2}}) 

	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def take(self, ctx, amount: int = None):
	# 	if ctx.channel.id != 777:

	# 		if amount is None:
	# 			emb = discord.Embed(description = 'Укажите сумму!')
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)
	# 		else:
	# 			if not clan.count_documents({"owner": ctx.author.id}):
	# 				emb = discord.Embed(description = 'Только глава клана может взять деньги из клановой казны!', timestamp = datetime.datetime.utcnow())
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)

	# 			else:

	# 				name = clan2.find_one({"_id": ctx.author.id})['name']

	# 				cash = clan.find_one({"name": name})['cash']

	# 				if cash < amount:
	# 					emb = discord.Embed(description = 'Сумма перевода больше суммы баланса клановой казны!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)
	# 				else:

	# 					emb = discord.Embed(description = f'Вы успешно перевели себе <a:currency:737351940320657588> {amount}', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)
						
	# 					balance = db['test']

	# 					newcash1 = clan.find_one({"name": name})['cash'] - amount
	# 					clan.update_one({"name": name}, {"$set": {"cash": newcash1}}) 
				
	# 					newcash2 = balance.find_one({"_id": ctx.author.id})['cash'] + amount
	# 					balance.update_one({"_id": ctx.author.id}, {"$set": {"cash": newcash2}}) 
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

	# @clan.command()
	# async def rename(self, ctx, *, name = None):
	# 	if ctx.channel.id != 777:

	# 		if name is None:
	# 			emb = discord.Embed(description = 'Введите название клана!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		elif len(name) > 25:
	# 			emb = discord.Embed(description = 'Имя клана слишком длиное!', timestamp = datetime.datetime.utcnow())
	# 			emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 			await ctx.send(embed = emb)

	# 		else:
					
	# 			if not clan2.count_documents({"_id": ctx.author.id}):
	# 				emb = discord.Embed(description = 'Вы не в клане!')
	# 				emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 				await ctx.send(embed = emb)
	# 			else:
	# 				if not clan.count_documents({"owner": ctx.author.id}):
	# 					emb = discord.Embed(description = 'Только глава может изменить имя клана!', timestamp = datetime.datetime.utcnow())
	# 					emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 					await ctx.send(embed = emb)

	# 				else:
	# 					if clan.count_documents({"name": name}):
	# 						emb = discord.Embed(description = 'Такой клан уже существует!', timestamp = datetime.datetime.utcnow())
	# 						emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 						await ctx.send(embed = emb)
	# 					else:

	# 						balance = db['test']
	# 						result = balance.find_one({"_id": ctx.author.id})['cash']
	# 						if result > 4000:
	# 							emb = discord.Embed(description = f'Вы изменили имя клана на **{name}**', timestamp = datetime.datetime.utcnow())
	# 							emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
								
	# 							await ctx.send(embed = emb)
								
	# 							names = clan2.find_one({"_id": ctx.author.id})['name']
	# 							clan.update_one({"name": names}, {"$set": {"name": name}}) 
	# 							for x in clan2.find({"name": names}):
	# 								clan2.update_one({"name": names}, {"$set": {"name": name}}) 

	# 							newcash2 = balance.find_one({"_id": ctx.author.id})['cash'] - 4000
	# 							balance.update_one({"_id": ctx.author.id}, {"$set": {"cash": newcash2}}) 

	# 						else:
	# 							emb = discord.Embed(description = 'Недостаточно денег!', timestamp = datetime.datetime.utcnow())
	# 							emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
	# 							await ctx.send(embed = emb)
	# 	else:
	# 		await ctx.message.add_reaction('❌')

	# 		await asyncio.sleep(5)
	# 		await ctx.message.delete()

def setup(bot):
    bot.add_cog(MainCog(bot))