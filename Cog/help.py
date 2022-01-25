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
from functions import functions as funs
import config

client = funs.mongo_c()
db = client.bot
servers = db.servers
settings = db.settings

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["помощь", "h", "рудз", 'хелп'], description='Команда помощи.', usage = '-')
    async def help(self, ctx, *, command = None):
        server = servers.find_one({'server':ctx.guild.id})
        if command != None:
            com = self.bot.get_command("".join(command))
            if com != None:

                emb = discord.Embed(title = f"❔ | Команда {com.name}\n" , description = f'{com.description}',
                color=server['embed_color'])
                emb.set_footer(text = '() - обязательный аргумент, [] - необязательный аргумент')
                emb.add_field(name = 'Использование', value = f'`{ctx.prefix}{com.name} {com.usage}`')

                if com.aliases != []:
                    emb.add_field(name = 'Альтернативные н.', value = f'{", ".join(com.aliases)}')
                if com.help != None:
                    emb.add_field(name = 'Категория', value = f'{com.help}')

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

            ct_d = {
            'bs': ['🖼', 'Фоны', 'Команды относящиеся к покупке и установке фонов.'],
            'clubs': ['🏰', 'Клубы', 'Команды относящиеся к управлению / настройке клубов.'],
            'economy': ['<:pokecoin:780356652359745537>', 'Экономика', 'Команды относящиеся к экономике. Игры, магазин, взаимодействие.'],
            'info': ['🧾', 'Информация', 'Команды для получения информации о сервере и пользователях.'],
            'mod': ['🔑', 'Модерация', 'Команды для управления пользователями и наказаниями.'],
            'profile': ['🎴', 'Профиль', 'Команды для просмотра профиля и взаимодействия с ним.'],
            'reactions': ['☠', 'Реакции', 'RP (role play) реакции для более живого общения!'],
            'remain': ['🥢', 'Команды без категории', 'Команды которые не нашли себе место среди других.'],
            'rpg': ['🏹', 'РПГ', 'Команды для настройки и игры в РПГ.'],
            'settings': ['🔧', 'Настройки', 'Команды для управления всеми системами бота.'],
            'voice': ['🔊', 'Управление приватками', 'Команды для управления приватными войс каналами.'],
            }

            for c in ct_d:
                i = ct_d[c]
                emb.add_field( name = f'{i[0]} | {i[1]}', value = i[2], inline = True  )

            options = []
            options.append(discord.SelectOption(label = "Главная", emoji = "🍡" ))
            for cc in ct_d.keys():
                i = ct_d[cc]
                options.append(discord.SelectOption(label = i[1], emoji = i[0] ))

            def embed(c_n):
                nonlocal ct_d
                nonlocal cogs
                nonlocal ctx
                nonlocal emb

                if c_n == 'Главная':
                    semb = emb

                else:
                    for i in ct_d:
                        c = ct_d[i]
                        if c[1] == c_n:
                            i_l = c
                            cog = cogs[i]

                    text = ''

                    for i in cog['commands']:
                        text += f'{ctx.prefix}{i} {i.usage}\n\n'

                    semb = discord.Embed(title = f'{i_l[0]} | {i_l[1]}', description = f"{i_l[2]}\nДля просмотра подробной информации о команде, пропишите\n {ctx.prefix}help (command)\n\n{text}" ,color=server['embed_color'])

                    if len(cog.keys()) != 1:
                        for i in cog.keys():
                            if i != 'commands':
                                t = ''
                                for n in cog[i]:
                                    t += f'{ctx.prefix}{n} {n.usage}\n\n'
                                semb.add_field( name = f'{i}', value= f"{t}", inline = True  )

                    semb.add_field( name = f'Инфорация об аргументах', value= f"Скобки при использовании команды указывать НЕ НАДО\n() - обязательный аргумент\n[] - необзательный аргумент\n / - выберите одно из двух\n<= меньше или равно\n", inline = True  )

                return semb

            class Dropdown(discord.ui.Select):
                def __init__(self, ctx, msg, options, placeholder, min_values, max_values:int, rem_args):
                    super().__init__(placeholder=placeholder, min_values=min_values, max_values=min_values, options=options)

                async def callback(self, interaction: discord.Interaction):
                    if ctx.author.id == interaction.user.id:
                        await msg.edit(embed = embed(self.values[0]))

                    else:
                        await interaction.response.send_message(f'Жми на свои кнопки!', ephemeral = True)


            class DropdownView(discord.ui.View):
                def __init__(self, ctx, msg, options:list, placeholder:str, min_values:int = 1, max_values:int = 1, timeout: float = 120.0, rem_args:list = []):
                    super().__init__(timeout=timeout)
                    self.add_item(Dropdown(ctx, msg, options, placeholder, min_values, max_values, rem_args))

                async def on_timeout(self):
                    self.stop()
                    await msg.edit(view = None)

            msg = await ctx.send(embed = emb)
            await msg.edit(view=DropdownView(ctx, msg, options = options, placeholder = '❓ | Выберите категорию', min_values = 1, max_values=1, timeout = 120.0, rem_args = []))


def setup(bot):
    bot.add_cog(help(bot))
