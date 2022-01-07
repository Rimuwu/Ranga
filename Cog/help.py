import nextcord as discord
from nextcord.ext import tasks, commands
import io
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import pprint

sys.path.append("..")
from ai3 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
servers = db.servers
settings = db.settings

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["помощь", "h", "рудз", 'хелп'], description='Команда помощи.')
    async def help(self,ctx, command = None):
        server = servers.find_one({'server':ctx.guild.id})
        if command != None:
            com = self.bot.get_command(command)
            if com != None:
                if com.aliases != []:
                    text = f'{com.description}\n**Другие названия:** {", ".join(com.aliases)}'
                else:
                    text = f'{com.description}'
                if com.help != None:
                    text += f'\n\n{com.help}'

                emb = discord.Embed(title=f"Команда {com.name}", description = f"Использование: **{ctx.prefix}{com.name}** `{com.usage}`\n{text}" ,color=server['embed_color']).set_footer(text = '() - обязательный аргумент, [] - необязательный аргумент')
                await ctx.send(embed=emb)
            else:
                await ctx.send("Комманда не найдена!")

        if command == None:
            emb = discord.Embed(title="Команды", description = f"Префикс {ctx.prefix}\nДля просмотра подробной информации пропишите {ctx.prefix}help (command)" ,color=server['embed_color'])
            cogs = {}
            for c in self.bot.commands:
                if c.hidden != True:
                    if c.name != 'help':
                        try:
                            cogs[c.cog_name]
                        except:
                            cogs.update({ c.cog_name: { 'commands': [] } })

                        if c.help == None:
                            cogs[c.cog_name]['commands'].append(c)

                        if c.help != None:
                            try:
                                cogs[c.cog_name][c.help].append(c)
                            except:
                                cogs[c.cog_name].update({ c.help: [c] })


            sections = {
            'bs': 'Фоны',
            'clubs': 'Клубы',
            'economy': 'Экономика',
            'info': 'Информация',
            'mod': 'Модерация',
            'profile': 'Профиль',
            'reactions': 'Реакции',
            'remain': 'Остальное',
            'rpg': 'Продвинутая экономика',
            'settings': 'Настройки',
            'voice': 'Управление приватками'
            }

            s_keys = sorted(cogs.keys())

            for key in s_keys:
                commands = []
                if len(cogs[key].keys()) > 1:
                    for k in cogs[key].keys():
                        if k != 'commands':
                            for c in cogs[key][k]:
                                commands.append(c.name)

                for i in cogs[key]["commands"]:
                    commands.append(i.name)


                text = ''
                text2 = ''

                for i in sorted(commands):
                    if len(text) > 1000:
                        text2 += f' `{i}` \n'
                    else:
                        text += f' `{i}` \n'

                emb.add_field( name = f'{sections[key]}', value= f"{text}", inline = True  )

                if text2 != '':
                    emb.add_field( name = f'{sections[key]} 2', value= f"{text2}", inline = True  )

            emb.set_footer(text = 'Для просмотра информации по категориям кликайте ◀ ▶')
            msg = await ctx.send(embed = emb)

            def embed(number):
                nonlocal sections
                nonlocal s_keys
                nonlocal cogs
                nonlocal server
                nonlocal ctx
                cog = cogs[s_keys[number]]
                text = ''

                for i in cog['commands']:
                    text += f'{ctx.prefix}{i} {i.usage}\n\n'

                emb = discord.Embed(title = sections[s_keys[number]] , description = f"**Для просмотра подробной информации пропишите {ctx.prefix}help (command)**\n\n{text}" ,color=server['embed_color'])

                if len(cog.keys()) != 1:
                    for i in cog.keys():
                        if i != 'commands':
                            t = ''
                            for n in cog[i]:
                                t += f'{ctx.prefix}{n} {n.usage}\n\n'
                            emb.add_field( name = f'{i}', value= f"{t}", inline = True  )

                if number + 1 == len(s_keys):
                    ss = 0
                else:
                    ss = number + 1

                if number - 1 == 0:
                    s = len(s_keys) - 1
                else:
                    s = number - 1

                emb.set_footer(text = f'Кликайте ({sections[s_keys[s]]}) ◀ ▶ ({sections[s_keys[ss]]}) [{s_keys.index(s_keys[number]) +1} | {len(s_keys)}]')
                emb.add_field( name = f'Инфорация об аргументах', value= f"Скобки при использовании команды указывать НЕ НАДО\n() - обязательный аргумент\n[] - необзательный аргумент\n / - выберите одно из двух\n<= меньше или равно\n", inline = True  )


                return emb

            solutions = ['◀', '▶', '❌']
            member = ctx.author
            reaction = 'a'

            number = -1

            def check( reaction, user):
                nonlocal msg
                return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

            async def rr():
                nonlocal reaction
                nonlocal number
                nonlocal s_keys

                if str(reaction.emoji) == '◀':
                    await msg.remove_reaction('◀', member)
                    number -= 1
                    if number > 0:
                        await msg.edit(embed = embed(number))
                        await reackt()
                    else:
                        number = len(s_keys) -1
                        await msg.edit(embed = embed(number))
                        await reackt()

                elif str(reaction.emoji) == '▶':
                    await msg.remove_reaction('▶', member)
                    number += 1
                    if number == len(s_keys):
                        number = 0
                        await msg.edit(embed = embed(number))
                        await reackt()
                    else:
                        await msg.edit(embed = embed(number))
                        await reackt()

                elif str(reaction.emoji) == '❌':
                    await msg.clear_reactions()
                    return

            async def reackt():
                nonlocal reaction
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    return
                else:
                    await rr()
            try:
                for x in solutions:
                    await msg.add_reaction(x)
                await reackt()
            except:
                return


def setup(bot):
    bot.add_cog(help(bot))
