# -*- coding: utf-8 -*-
import nextcord as discord
from nextcord.ext import tasks, commands
# from discord_slash import SlashCommand, SlashContext
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO
import random
from random import choice
import asyncio
import time
from datetime import datetime, timedelta
import os
import pymongo
import math
from fuzzywuzzy import fuzz
import config
import pprint
import os


client = pymongo.MongoClient(config.cluster_token)
db = client.bot

users = db.users
backs = db.bs
servers = db.servers
clubs = db.clubs
frames = db.frames
settings = db.settings

peoplesCD = {}
start_time = time.time()

# префикс ======================================= #

def get_prefix(client, message):
    global servers
    try:
        prefix_server = servers.find_one({"server": message.guild.id})["prefix"]
        return str(prefix_server)
    except:
        return "+"

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = get_prefix, intents = intents)
# slash = SlashCommand(bot, sync_commands=True)


# функции ======================================= #

class functions:

    @staticmethod
    def time_end(seconds:int):
        mm = int(seconds//2592000)
        seconds -= mm*2592000
        w = int(seconds//604800)
        seconds -= w*604800
        d = int(seconds//86400)
        seconds -= d*86400
        h = int(seconds//3600)
        seconds -= h*3600
        m = int(seconds//60)
        seconds -= m*60
        s = int(seconds%60)

        if mm < 10:
            mm = f"0{mm}"
        if w < 10:
            w = f"0{w}"
        if d < 10:
            d = f"0{d}"
        if h < 10:
            h = f"0{h}"
        if m < 10:
            m = f"0{m}"
        if s < 10:
            s = f"0{s}"

        if m == '00' and h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{s}s"
        elif h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{m}m {s}s"
        elif d == '00' and w == '00' and mm == '00':
            return f"{h}h {m}m {s}s"
        elif w == '00' and mm == '00':
            return f"{d}d {h}h {m}m {s}s"
        elif mm == '00':
            return f"{w}w {d}d {h}h {m}m {s}s"
        else:
            return  f"{mm}M {w}w {d}d {h}h {m}m {s}s"

    @staticmethod
    def text_replase(text:str, member: discord.Member = None):
        if text == 'text':
            text = "Доступные теги:\n`{member.mention}` - упоминает пользователя\n`{member.name}` - отображает имя пользователя\n`{member.tag}` - отображает тег пользователя (6228)\n`{member.name.tag}` - отображает имя и тег пользователя (имя#0000)\n`{guild.name}` -  отображает имя сервера\n`{members}` - отображает колличество пользователей на сервере\n`{members.ordinal}` - отображает колличество пользовталей с окончанием (668-ой)\n`{time}` - указывает время на момент события (24:61 31.02.3021)\n`{premium_subscribers}` - указывает число бустов\n`{boost.role}` - упоминает системную роль бустеров\n`{member.lvl}` - уровень пользователя\n`{member.money}` - монеты пользователя\n`{member.xp}` - опыт полльзователя"
            return text

        Time = time.strftime('%H:%M %d.%m.%Y')
        try:
            n = int(len(member.guild.members))
            n = int(math.log10(n))
            ord = int(str(len(member.guild.members))[n:])
            if ord == 0 or ord == 1 or ord == 4 or ord == 5 or ord == 9:
                ord = "ый"
            elif ord == 2 or ord == 6 or ord == 7 or ord == 8:
                ord = "ой"
            elif ord == 3:
                ord = "ий"
            if member != None:
                user = functions.user_check(member, member.guild)
                text = text.replace('{member.mention}', f'{member.mention}')
                text = text.replace('{member.name}', f'{member.name}')
                text = text.replace('{member.tag}', f'{member.discriminator}')
                text = text.replace('{member.name.tag}', f'{member.name}#{member.discriminator}')
                text = text.replace('{guild.name}', f'{member.guild.name}')
                text = text.replace('{members}', f'{len(member.guild.members)}')
                text = text.replace('{premium_subscribers}', f'{len(member.guild.premium_subscribers)}')
                text = text.replace('{members.ordinal}', f'{len(member.guild.members)}-{ord}')
                text = text.replace('{member.money}', f'{user["money"]}')
                text = text.replace('{member.lvl}', f'{user["lvl"]}')
                text = text.replace('{member.xp}', f'{user["xp"]} / { 5 * user["lvl"]*user["lvl"] + 50 * user["lvl"] + 100}')
            text = text.replace('{time}', f'{Time}')

            if text.find('{boost.role}') != -1:
                try:
                    text = text.replace('{boost.role}', f'{member.guild.premium_subscriber_role.mention}')
                except Exception:
                    pass
            return text
        except Exception:
            return text

    @staticmethod
    def user_check(user:discord.Member, guild: discord.Guild, met:str = None, key:str = 'users'):

        def upd(server):
            return {
                    "money": server['economy']['start_money'],

                    "lvl": 0,
                    'xp': 0,

                    'voice_time': 0,
                    'voice_lvl': 0,
                    'voice_xp': 0,

                    'inv': [],
                    'gm_status': False,

                    'cache': {
                               'week_act': [0, None],
                    },

                    'guild': None,
                    'Nitro': False,
                    'back': 0,
                    'back_inv': [0],
                    'rep': [[],[]],
                   }

        if type(guild) == int:
            guild.id = guild

        server = servers.find_one({"server": guild.id})
        if met == None:

            try:
                user = server[key][str(user.id)]
                return user
            except Exception:
                if user.bot == True:
                    return False

                a = server[key].copy()
                a.update({ str(user.id): upd(server) })
                servers.update_one({"server": guild.id}, {"$set": {key: a}})
                return a[str(user.id)]

        if met == 'dcheck':

            try:
                user = server[key][str(user.id)]
                return True
            except Exception:
                return False

        if met == 'add':

            a = server[key].copy()
            a.update({str(user.id): upd(server) })
            servers.update_one({"server": guild.id}, {"$set": {key: a}})
            return True


    @staticmethod
    def change_race(member:discord.Member, guild:discord.Guild, race:str):

        server = servers.find_one({"server": guild.id})
        user = functions.user_check(member, guild)

        if member.bot == True:
            return False

        r = server['races'][race]
        a = server['users']
        pprint.pprint(a[str(member.id)])
        a[str(member.id)].update({

        'hp': r['hp'], 'hpmax': r['hp'],
        'mana': r['mana'], 'manamax': r['mana'],
        "pet": None, "weapon": None, 'armor': None,

        'rpg_lvl': 0, 'rpg_xp': 0,
        'bio': None, 'people_avatar': None,

        'race': race,
        'gm_status': True,
        })

        if r['items'] != None:
            for i in r['items']:
                a[str(member.id)]['inv'].append(functions.creat_item(guild.id, i))

        pprint.pprint(a[str(member.id)])

        servers.update_one({"server": guild.id}, {"$set": {"users": a}})
        return a[str(member.id)]

    @staticmethod
    def user_update(user, guild: discord.Guild, key:str, ch, met = 'update', key2 = 'users'):
        server = servers.find_one({"server": guild.id})
        a = server[key2].copy()

        if type(user) == discord.Member:
            user_id = user.id
        else:
            user_id = user

        if type(guild) == int:
            guild.id = guild

        if met == 'update':

            try:
                a[str(user_id)].update({key : ch })
            except Exception:
                a.update({str(user_id) : {key : ch } })

            servers.update_one({"server": guild.id}, {"$set": {key2: a}})
            return True

        if met == 'pop':

            try:

                a[str(user_id)].pop(key)
                if a[str(user_id)] == {}:
                    a.pop(str(user_id))

                servers.update_one({"server": guild.id}, {"$set": {key2: a}})
                return True

            except Exception:
                return False
        else:
            print(f'Метод {met} не найден')

    @staticmethod
    def roles_check(user:discord.Member, guild_id:int):
        roles = user.roles
        list_roles = []
        server = servers.find_one({"server": guild_id})


        if user.id == 323512096350535680: #для помощи другим пользователям в настройке
            return True

        try:

            if server['mod']['admin_roles'] == []:
                if user.guild_permissions.administrator == True:
                    return True
                else:
                    return False
            else:
                for role in roles:
                    list_roles.append(role.id)
                result = list(set(server['mod']['admin_roles']) & set(list_roles))
                if result != []:
                    return True
                else:
                    return False

        except Exception:
            if user.guild_permissions.administrator == True:
                return True
            else:
                return False

    @staticmethod
    def cooldown_check(user:discord.Member, guild:discord.Guild, command:str, met:str, rest = False):
        server = servers.find_one({"server": guild.id})

        #Выводим True если у пользователя активный кулдаун, False если пользователя нет в словаре

        try:
            cl = server['mod']['cooldowns']
            cc = server['mod']['cooldowns'][str(command)]
        except Exception:
            return False

        if met == 'check':
        #Выводим True если у пользователя активный кулдаун, False если у пользователя нет кулдауна

            if cc['type'] == 'users':

                try:
                    cc['users'][str(user.id)]
                except Exception:
                    return False

                if cc['users'][str(user.id)] < time.time():
                    cl[str(command)]['users'].pop(str(user.id))
                    server['mod'].update({"cooldowns": cl})
                    servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                    return False
                else:
                    return True

            if cc['type'] == 'server':

                if cc['server_c'] < time.time():
                    cl[str(command)].update({'server_c': 0 })
                    server['mod'].update({"cooldowns": cl})
                    servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                    return False
                else:
                    return True

            if cc['type'] == 'roles':
                roles_id = []

                for i in user.roles:
                    roles_id.append(i.id)

                if cc['role'] in roles_id:

                    if cc['role_c'] < time.time():
                        cl[str(command)].update({'role_c': 0 })
                        server['mod'].update({"cooldowns": cl})
                        servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                        return False
                    else:
                        return True
                else:
                    return False

        if met == 'add':
            #Выводим True если пользователю был добавлен кулдаун

            if cc['type'] == 'users':
                cl[str(command)]['users'].update({str(user.id): int(time.time() + cc['time']) })
                server['mod'].update({"cooldowns": cl})
                servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                return True

            if cc['type'] == 'server':
                cl[str(command)].update({'server_c': int(time.time() + cc['time']) })
                server['mod'].update({"cooldowns": cl})
                servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                return True

            if cc['type'] == 'roles':
                cl[str(command)].update({'role_c': int(time.time() + cc['time']) })
                server['mod'].update({"cooldowns": cl})
                servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                return True

        if met == 'reset':
            #Выводим True если пользователю был сброшен кулдаун, False если пользователя нет в списке
            #Если rest = False то сбрасывается только 1 пользователь, иначе полностью

            if cc['type'] == 'users':

                if rest == False:

                    try:
                        cc['users'][str(user.id)]
                    except Exception:
                        return False

                    cl[str(command)]['users'].pop(str(user.id))
                    server['mod'].update({"cooldowns": cl})
                    servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                    return True

                else:

                    cl[str(command)].update({'users':{}})
                    server['mod'].update({"cooldowns": cl})
                    servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                    return True


            if cc['type'] == 'server':
                cl[str(command)].update({'server_c': 0 })
                server['mod'].update({"cooldowns": cl})
                servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                return True

            if cc['type'] == 'roles':
                roles_id = []

                for i in user.roles:
                    roles_id.append(i.id)

                if cc['role'] in roles_id:

                    cl[str(command)].update({'role_c': 0 })
                    server['mod'].update({"cooldowns": cl})
                    servers.update_one({"server": guild.id}, {"$set": {'mod': server['mod']}})
                    return True
                else:
                    return False

    @staticmethod
    def insert_server(guild):
        server = {

            "server": guild.id,
            'prefix': "+",
            "upsend_sett": {'emb_st': False,
                            'up_message': None,
                            "upitems":{},
                            "upsend": None,
                            'image_url': None,
                            'type': 'png',
                           },

            'voice': {'voice_category': None,
                      'voice_channel': None,
                      'private_voices': {},
                      'randomc_channel': None,
                      'rc_bl_channels': None
                     },

            'send':{"joinsend": None, "leavensend": None
                   },

            'welcome':{},
            'goodbye':{},

            'emoji': {'emoji_channel': None,
                      'emojis': []
                     },

            'mod': {'black_channels': [], #в каналах бот не работает
                    'off_commands': [], # не отвечает на команды
                    'cooldowns': {

                                    'daily': {
                                        'type': 'users',
                                        'time': 82800,
                                        'users': {},
                                             },

                    }, #ожидания на команды
                    'admin_roles': [], #роли с право настраивать модерировать
                    'warns': {}, #варны
                    'muterole': None, #роль мьюта
                    'punishments_warns': {}, #наказания за варны

                    'flud_shield': {}, #защита от флуда
                    'bad_words': {}, #защита от слов
                    'media_channels': {}, #канал в которых не может быть текста
                    'members_mention': {}, #отслеживание упоминаний пользовталей
                    'roles_mention': {}, #отслеживание упоминаний ролей
                    'wlist_roles': [], #роли на которые не реагирует автомод
                    'wlist_members': [], #пользователи на которых не реагирует автомод
                    'log_channel': {}, #канал логирования
                    'delete_command': None, #настройка удаления команды после использования
                    'flud_ch_nor': [],

                   },

            'mute_members': {},

            'rr': {},
            'boost':{    'send':None,
                         'description': None,
                         'footer':None,
                         'url': None,
                         'reward': [],
                    },

            'users': {},
            'save_users': {},

            'economy': { 'currency': "<:pokecoin:780356652359745537>",
                         'start_money': 0,
                         'gl_shop': {},
                         'daily_reward': {},
                         'lvl_xp': 20,
                         'games': {

                                    'blackjack': {
                                        'mini': 100,
                                        'max': 10000,
                                        'percent': 1.25,
                                        },

                                    'slots': {
                                        'mini': 100,
                                        'max': 10000,
                                        'percent': 3.0,
                                        },

                                    'chance': {
                                        'mini': 100,
                                        'max': 10000,
                                        },
                                  },
                       },
            'roles_income': {},

            'races': {},
            'items': {},

            'embed_color': 0xf03e65,
            'banner_status': False,
            'pizza_board': {'channel':None,
                            'messages': {},
                           },
            'tickets': {},

            'save': {'name_save': False,
                     'roles_save': False,
                     'date_save': False,
                    },
            'voice_reward': {},

            'rpg': {
                'iid': 0,
                'locations': {},
                'mobs': {},
                'boss': {},
                'raids-boss': {},
                'guilds': {},
                'settings': {},
                'effects': {},

            },

        }
        servers.insert_one(server)
        return True

    @staticmethod
    async def warn(ctx, user, reason, warn_author):

        server = servers.find_one({'server':ctx.guild.id})
        wtext = 'Ничего'

        try:
            l = server['mod']['warns'][f'{user.id}']
            list = []
            for i in l.keys():
                list.append(int(i))
            l = max(list)+1
        except Exception:
            l = 1

        if reason != None:
            if len(reason) > 200:
                await ctx.send(f"Причина более 200 символов, будте более кратки, в данный момент длинна {len(reason)} символов")
                return
        try:
            server['mod']['warns'][str(user.id)]
        except KeyError:
            server['mod']['warns'][str(user.id)] = {}
        server['mod']['warns'][str(user.id)].update({str(l): {'reason':reason,'time': str(datetime.now().strftime("%Y-%m-%d.%H:%M:%S")),'author':warn_author.id}})
        servers.update_one({'server':ctx.guild.id},{"$set": {'mod': server['mod'] }})
        try:
            punishment = server['mod']['punishments_warns'][f"{l}"]
            pun = punishment["punishment"]

        except Exception:
            pun = 0

        if pun == 0: #ничего
            wtext = 'Ничего'

        elif pun == 1: #мьют
            try:
                await user.add_roles(bot.get_guild(ctx.guild.id).get_role(server['mod']['muterole']))
                a = server['mute_members']
                a.update({str(user.id): time.time() + punishment['time'] })
                servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
                ttt = functions.time_end(time.time() + punishment['time'])
                wtext = f'Мьют: `{ttt}`'
            except Exception:
                await ctx.send("Роль мьюта не настроена")

        elif pun == 2: #кик
            wtext = f'Кик'
            try:
                await user.kick(reason=f"Авто пинок за варн #{l}")
            except Exception:
                await ctx.send("У бота недостаточно прав на кик пользоавтеля")

        elif pun == 3: #бан
            wtext = f'Бан'
            try:
                await user.ban(reason=f"Авто блокировка за варн #{l}")
            except Exception:
                await ctx.send("У бота недостаточно прав на бан пользоавтеля")

        elif pun == 4: #выдача роли
            role = discord.utils.get(ctx.guild.roles, id = punishment['roleadd']) #id роли
            wtext = f'Добавление роли {role.mention}'
            try:
                await user.add_roles(role)
            except Exception:
                pass

        elif pun == 5: #удаление роли
            role = discord.utils.get(ctx.guild.roles, id = punishment['roleremove']) #id роли
            wtext = f'Удаление роли {role.mention}'
            try:
                await user.remove_role(role)
            except Exception:
                pass

        elif pun == 6: #сообщение
            await ctx.send(f"{punishment['message']}")
            wtext = 'Сообщение'

        embd = discord.Embed(title = f"Варн", description = f"Пользователю {user.mention} был выдан варн #{l}\nПричина: {reason}\nНаказание: {wtext}", color=0xf03e65)
        await ctx.send(embed = embd)

    @staticmethod
    def mongo_c():
        global client
        return client

    @staticmethod
    async def reactions_check(solutions: list, member: discord.Member, msg: discord.Message, clear:bool = False, timeout:float = 30.0):

        def check(reaction, user):
            nonlocal msg
            return user == member and str(reaction.emoji) in solutions and reaction.message == msg

        async def reackt():
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return 'Timeout'
            else:
                if reaction.emoji in solutions:
                    if clear == False:
                        await msg.remove_reaction(str(reaction.emoji), member)
                    else:
                        await msg.clear_reactions()

                    return reaction

        for x in solutions:
            await msg.add_reaction(x)

        return await reackt()

    @staticmethod
    def creat_item(guild_id:int, item_id:int):
        server = servers.find_one({'server': guild_id})
        rpg = server['rpg']
        iid = rpg['iid'] + 1

        try:
            item = server['items'][str(item_id)]
        except:
            print('Объект не найден')
            return {}

        item.update({'iid': iid})
        rpg.update({'iid': iid})

        servers.update_one({"server": guild_id}, {"$set": {"rpg": rpg}})
        return item

    @staticmethod
    def item_info(item, guild_id:int):
        server = servers.find_one({'server': guild_id})

        ni = {}
        ni['name'] = item['name']
        ni['image'] = item['image']

        try:
            ni['emoji'] = item['emoji']
        except:
            ni['emoji'] = "🏮"

        if item['description'] != None:
            ni['description'] = item['description']
        else:
            ni['description'] = '*Засекречено* | (отсутствует)'


        try:
            f = item['quality']
        except:
            item['quality'] = '<:void:924632079143157800>'

        if item['quality'] == 'n':
            ni['quality'] = '<:normal_q:781531816993620001>'
        elif item['quality'] == 'u':
            ni['quality'] = '<:unusual_q:781531868780691476>'
        elif item['quality'] == 'r':
            ni['quality'] = '<:rare_q:781531919140651048>'
        elif item['quality'] == 'o':
            ni['quality'] = '<:orate_q:781531996866084874>'
        elif item['quality'] == 'l':
            ni['quality'] = '<:legendary_q:781532085130100737>'


        try:
            tt = ", ".join(item['race_u'])
            ni['race_u'] = f"Расы которые могут использовать: {tt}"
        except:
            ni['race_u'] = 'Все расы могут использовать данный предмет.'


        try:
            el = item['element']
        except:
            el = None

        if el == 'w':
            ni['element'] = '<:water:888029916287885332>'
        elif el == 'a':
            ni['element'] = '<:air:888029789749919787>'
        elif el == 'f':
            ni['element'] = '<:fire:888029761828425789>'
        elif el == 'e':
            ni['element'] = '<:earth:888029840945598534>'
        else:
            ni['element'] = 'Отсутствует'



        if item['type'] == 'eat':
            ni['type'] = '🍖 | Еда'
            ni['act_title'] = f'Питательность: {item["act"]}'

        elif item['type'] == 'point':
            ni['type'] = '<:mana:780352235246452756> | Зелье'
            if item['style'] == 'heal':
                ni['act_title'] = f"Восстановление {item['act']} здоровья"
            elif item['style'] == 'mana':
                ni['act_title'] = f"Восстановление {item['act']} маны"

        elif item['type'] == 'case':
            ni['type'] = '<:chest:827218232783405097> | Сундук сокровищ'
            ni['act_title'] = f'Выпадаемые предметы: {", ".join(server["items"][str(x)]["name"] for x in item["act"])}'

        elif item['type'] == 'armor':
            ni['type'] = '<:armor:827220888130682880> | Броня'
            if item['style'] == 'add':
                ni['act_title'] = f"Добавляет {item['act']} брони"
            elif item['style'] == 'set':
                ni['act_title'] = f"Устанавливает {item['act']} брони"

        elif item['type'] == 'weapon':
            if item['style'] == 'sword':
                ni['type'] =  f'<:katana:827215937677426738> | Оружие ближнего боя'

                if item['stabl'] == 0:
                    st = 'Неразрушаемый'
                else:
                    st = item['stabl']
                ni['act_title'] = f"Атакует с максимальным уроном {item['act']}\nПрочность: {st}"

            if item['style'] == 'staff':
                ni['type'] =  f'<:staff:827215895548919869> | Оружие магического типа'
                ni['act_title'] = f"Атакует с максимальным уроном {item['act']}\nИспользует {item['mana_use']} маны"

            if item['style'] == 'bow':
                ni['type'] = f'<:longrangeweapon:827217317544984607> | Оружие дальнего боя'
                ni['act_title'] = f"Атакует с максимальным уроном {item['act']}\nИспользует {server['items'][str(item['bow_item'])]['name']} для стрельбы"

        elif item['type'] == 'pet':
            ni['type'] = '<:pet:780381475207905290> | Питомец'
            if item['style'] == 'hp+':
                ni['act_title'] = f"Увеличивает здоровье на {item['act']}"
            elif item['style'] == f'mana+':
                ni['act_title'] = f"Увеличивает ману на {item['act']}"
            elif item['style'] == f'damage+':
                ni['act_title'] = f"Увеличивает урон на {item['act']}"
            elif item['style'] == f'armor+':
                ni['act_title'] = f"Увеличивает защиту на {item['act']}"
            elif item['style'] == f'mana-':
                ni['act_title'] = f"Уменьшает расход маны на {item['act']}"

        elif item['type'] == 'material':
            ni['type'] = '<:leather:783036521099034626> | Материал'
            ni['act_title'] = 'Материал может быть использован в крафтах'

        elif item['type'] == 'recipe':
            ni['type'] = '<:recipe:827221967886745600> | Рецепт'
            c_i = []
            ni_i = []
            ct_i = []
            for i in item['act']:
                c_i.append(server['items'][str(i)]['name'])

            for n in item['ndi']:
                ni_i.append(server['items'][str(n)]['name'])

            for c in item['ndi']:
                ct_i.append(server['items'][str(n)]['name'])


            ni['act_title'] = f"Выпадаемые предметы: {', '.join(c_i)}\n"
            if ni_i != []:
                ni['act_title'] += f'Предметы которые не будут удалены: {", ".join(ni_i)}\n'

            ni['act_title'] += f'Создаваемыве предметы: {", ".join(ct_i)}'


        elif item['type'] == 'role':
            ni['type'] = '<:icons8pokeball96:779718625459437608> | Роль'
            if item['style'] == f'add':
                ni['act_title'] = f"Добавляет вам <@{item['act']}>"
            elif item['style'] == f'remore':
                ni['act_title'] = f"Удаляет у вас <@{item['act']}>"

        elif item['type'] == 'prop':
            ni['type'] = '📦 | Проп'
            ni['act'] = 'Является неиграбельным предметом'



        return ni


# коги ======================================= #

bot.remove_command( "help" )

for filename in os.listdir("./Cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cog.{filename[:-3]}")

    else:
        if os.path.isfile(filename):
            print(f"Unable to load {filename[:-3]}")


# slash ====================================== #

# @slash.slash(name = 'lock',description="Закрыть приватный канал для всех или для определённого пользователя")
# async def voice_lock(ctx, member:discord.Member = None):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.reply("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.reply("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         if member != None:
#             await channel.set_permissions(member, connect=False)
#             emb = discord.Embed(description = f'Канал был закрыт для подключения пользователем {member.mention}!', color=0xf03e65)
#
#         else:
#             await channel.set_permissions(ctx.guild.default_role, connect=False)
#             emb = discord.Embed(description = 'Канал был закрыт для подключения пользователей!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.reply(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'unlock',description="Открыть приватный канал для всех или для определённого пользователя")
# async def voice_unlock(ctx, member:discord.Member = None):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await  bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         if member != None:
#             await channel.set_permissions(member, connect=True)
#             emb = discord.Embed(description = f'Канал был открыт для подключения пользователем {member.mention}!', color=0xf03e65)
#
#         else:
#             await channel.set_permissions(ctx.guild.default_role, connect=True)
#             emb = discord.Embed(description = 'Канал был открыт для подключения пользователей!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'hide',description="Скрыть приватный канал для всех или для определённого пользователя")
# async def voice_hide(ctx, member:discord.Member = None):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         if member != None:
#             await channel.set_permissions(member, view_channel=False)
#             emb = discord.Embed(description = f'Канал был закрыт для просмотра пользователем {member.mention}!', color=0xf03e65)
#
#         else:
#             await channel.set_permissions(ctx.guild.default_role, view_channel=False)
#             emb = discord.Embed(description = 'Канал был закрыт для просмотра пользователей!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'unhide',description="Показать приватный канал для всех или для определённого пользователя")
# async def voice_unhide(ctx, member:discord.Member = None):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await  bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         if member != None:
#             await channel.set_permissions(member, view_channel=True)
#             emb = discord.Embed(description = f'Канал был открыт для просмотра пользователем {member.mention}!', color=0xf03e65)
#
#         else:
#             await channel.set_permissions(ctx.guild.default_role, view_channel=True)
#             emb = discord.Embed(description = 'Канал был открыт для просмотра пользователей!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'kick',description="Выганть пользователя из приватного канала")
# async def voice_kick(ctx, member:discord.Member):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     if member.voice == None:
#         await ctx.send("Пользователь не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await  bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         await member.move_to(channel=None, reason="Пользователь кикнут создателем приватного войса")
#         emb = discord.Embed(description = f'{member.mention} был исключён из войса!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'owner',description="Передать управление войсом пользователю")
# async def voice_owner(ctx, member:discord.Member):
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     if member.voice == None:
#         await ctx.send("Пользователь не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await  bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         v = server['voice']['private_voices']
#         v.update({f"{channel.id}": member.id})
#         servers.update_one({'server': ctx.guild.id},{'$set': {'voice': {'private_voices': v} }})
#         emb = discord.Embed(description = f'{member.mention} теперь создатель войса!', color=0xf03e65)
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'limit',description="Установить лимит приватного войс-канала")
# async def voice_limit(ctx, limit:int):
#
#     if limit > 99:
#         limit = 99
#     elif limit < 1:
#         limit = 1
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         emb = discord.Embed(description = f'Лимит канала был установлен на {limit}!', color=0xf03e65)
#         await channel.edit(user_limit = limit ,reason="Настройка лимита приватного войса")
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)
#
# @slash.slash(name = 'name',description="Переименовать приватный войс-канал")
# async def voice_name( ctx, *,name:str):
#
#     if len(name) > 100:
#         await ctx.send("Название не может быть больше чем 100 символов!", delete_after = 5.0)
#         return
#     elif len(name) < 1:
#         await ctx.send("Название не может быть меньше чем 1 символ!", delete_after = 5.0)
#         return
#
#     try:
#         await ctx.channel.purge(limit = 1)
#     except Exception:
#        pass
#
#     server = servers.find_one({"server": ctx.guild.id})
#     if ctx.author.voice == None:
#         await ctx.send("Вы не в войс канале", delete_after = 5.0)
#         return
#     else:
#         channel = await bot.fetch_channel(ctx.author.voice.channel.id)
#         try:
#             channel_owner = server['voice']['private_voices'][f'{channel.id}']
#         except Exception:
#             await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
#             return
#
#         if channel_owner != ctx.author.id:
#             await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
#             return
#
#         emb = discord.Embed(description = f'Название канала было изменено на  {name}!', color=0xf03e65)
#         await channel.edit(name = name ,reason="Настройка названия приватного войса")
#
#         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
#         message = await ctx.send(embed = emb, delete_after = 5.0)

# event ====================================== #

@bot.event
async def on_connect():
    await bot.change_presence( status = discord.Status.online, activity = discord.Game('Demon strating...'))


async def global_chat(message, s, server):

    async def emb(word, server):
        embed = discord.Embed(title = f"Ошибка", description = f"Данное слово (`{word}`) запрещено в межсервереом чате!", color=0xf44a4a)
        webhook = await bot.fetch_webhook(server['globalchat']['webhook'])
        await webhook.send(username = "Система межсервера", avatar_url = 'https://img.icons8.com/dusk/64/000000/web-shield.png', embed=embed)

    try:
        if message.webhook_id == None:
            if message.author.bot == True: return
            #проверка на варны
            try:
                wmax = s['bl global chat'][str(message.author.id)][max(s['bl global chat'][str(message.author.id)].keys())]
                if time.time() < wmax['time']:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    return

            except Exception:
                pass
            #проверка на бан в межсервере
            try:
                s['bl global chat'][str(message.author.id)]['ban']
                try:
                    await message.delete()
                except Exception:
                    pass
                return

            except Exception:
                pass

            if message.channel.id == server['globalchat']['channel']:

                #проверка на слова
                for word in s['off-words']:
                    allword = ''
                    for spw in message.content.split():
                        allword = allword + spw
                        if fuzz.token_sort_ratio(word,allword) > 90:
                            await emb(word, server)
                            await message.delete()
                            return

                        if allword.find(str(word)) != -1:
                            await emb(word, server)
                            await message.delete()
                            return

                        if spw.find(str(word)) != -1:
                            await emb(word, server)
                            await message.delete()
                            return

                #проверка на флуд
                messages = await message.channel.history().flatten()
                l = []

                for mess in messages:
                    if mess.author.id == message.author.id:
                        if message.content != '':
                            l.append(mess)

                lm = []
                counter = 0
                m = []
                for i in l:
                    if counter != 3:
                        m.append(i)
                        lm.append(i.content)
                        counter += 1

                flud_p = 0
                for mes in lm:
                    if fuzz.token_sort_ratio(message.content, mes) > 80 or fuzz.ratio(message.content, mes) > 80:
                        flud_p += 1


                if flud_p >= 3:
                    for i in m:
                        try:
                            await i.delete()
                        except Exception:
                            pass


                    try:
                        id = message.author.id
                        reason = 'Auto flud warn'
                        s = settings.find_one({"sid": 1})
                        s['bl global chat'][str(id)]
                        nw = len(s['bl global chat'][str(id)].keys())

                        if nw < 3:
                            s['bl global chat'][str(id)].update({str(nw+1):{'reason':reason,"time":time.time() + 2628000}})
                            settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                            await message.channel.send(f"Пользователь c id `{id}` получил варн #{nw+1}\nПо причине: Auto flud warn")
                        else:
                            s['bl global chat'][str(id)].update({'ban':f'{reason} | auto ban due to 3 warns'})
                            settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                            await message.channel.send(f"Пользователь c id `{id}` был автоматически забанен за х3 предупреждения\nПо причине: Auto flud warn")


                    except Exception:
                        s['bl global chat'].update({str(id):{'1':{'reason':reason,"time":time.time() + 604800}}})
                        settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                        await message.channel.send(f"Пользователь c id `{id}` получил варн #1\nПо причине: Auto flud warn")



                try:
                    code = int(server['global_code'])
                except Exception:
                    code = 0

                if code == 0:
                    guilds = servers.find({'globalchat':{'$ne':None}})
                else:
                    guilds = servers.find({'global_code': code})

                for i in guilds:
                    try:
                        ccode = i['global_code']
                        if ccode == None:
                            ccode = 0
                    except Exception:
                        ccode = 0

                    try:
                        if i['server'] != server['server']:

                            if code == ccode:
                                try:
                                    y = 0
                                    try:
                                        webhook = await bot.fetch_webhook(i['globalchat']['webhook'])
                                        y = 1
                                    except Exception:
                                        y = 2

                                    if y == 1:
                                        await webhook.send(message.clean_content, files = [await a.to_file() for a in message.attachments], username = f"{message.author.name}#{message.author.discriminator}", avatar_url = message.author.avatar.url)
                                except Exception:
                                    pass

                    except Exception:
                        pass

                channel = await bot.fetch_channel(865527704085856256)
                try:
                    await channel.send(f'Имя: {message.author.name}#{message.author.discriminator}\nID: {message.author.id}\nСервер ID: {message.author.guild.id}\nCode: {code}\nКонтент: `{message.clean_content}`', files = [await a.to_file() for a in message.attachments])
                except Exception:
                    pass
    except Exception:
        pass

def cooldown(user_id, guild_id):
    # Возращаем True если пользователь может получить опыт, False если у пользователя есть задержка
    global peoplesCD

    try: #проверка
        if peoplesCD[str(guild_id)][str(user_id)] <= time.time():
            peoplesCD[str(guild_id)].pop(str(user_id))
            return True
        else:
            return False
    except Exception:
        pass

    try: #добавление при не наличии пользователя
        peoplesCD[str(guild_id)].update({ str(user_id): int(time.time()+60) })
        return True
    except Exception:
        pass

    try: #добавление при не наличии пользователя и сервера
        peoplesCD.update({ str(guild_id): {str(user_id): int(time.time()+60) } })
        return True
    except Exception:
        pass


async def lvl_up_image(message, user, server):

    server = servers.find_one({"server": message.guild.id})
    user = functions.user_check(message.author, message.guild)

    upitems = server["upsend_sett"]['upitems']
    UpSend = server["upsend_sett"]['upsend']
    ust = server["upsend_sett"]
    lvl = user['lvl']

    try:
        mr = upitems[str(lvl)]['money']
    except Exception:
        mr = 0
        lv = lvl
        while mr == 0:
            lv -= 1
            if lv != 0:
                try:
                    mr += upitems[str(lv)]['money']
                except:
                    pass
            if lv <= 0:
                mr = 350



    bal = random.randint(int(mr - mr / 100 * 50), mr)

    functions.user_update(message.author.id, message.guild, "xp", 0)
    functions.user_update(message.author.id, message.guild, "lvl", user['lvl']+1)

    functions.user_update(message.author.id, message.guild, "money", user['money']+bal)

    try:
        for i in upitems[str(lvl+1)]['items']:
            user['inv'].append(functions.creat_item(message.guild.id, i))
        functions.user_update(message.author.id, message.guild, "inv", user['inv'])
    except Exception:
        pass

    if UpSend == 777777777777777771 or UpSend == None:
        return


    def trans_paste(fg_img,bg_img,alpha=10,box=(0,0)):
        fg_img_trans = Image.new("RGBA",fg_img.size)
        fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
        bg_img.paste(fg_img_trans,box,fg_img_trans)
        return bg_img

    def prepare_mask(size, antialias = 2):
        mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2.5))
        return mask.resize(size, Image.ANTIALIAS)

    def crop(im, s):
        w, h = im.size
        k = w / s[0] - h / s[1]

        if k > 0:
            im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
        elif k < 0:
            im = im.crop((0, (h - w) / 2, w, (h + w) / 2))

        return im.resize(s, Image.ANTIALIAS)

    def bl_f(im):
        mask = Image.new('L',(720, 217))
        ImageDraw.Draw(mask).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = 250)
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        im.paste(im.filter( ImageFilter.GaussianBlur(radius=12) ), mask=mask)
        return im


    member = message.author

    alpha = Image.open('elements/alpha.png')
    alpha = alpha.resize((720, 217), Image.ANTIALIAS) # улучшение качества

    if server['upsend_sett']['image_url'] == None:
        listurl = [
        'https://ic.wampi.ru/2021/08/19/card-1.png',
        'https://ic.wampi.ru/2021/08/19/card-2.png',
        'https://ic.wampi.ru/2021/08/19/card-3.png',
        'https://ic.wampi.ru/2021/08/19/card-4.png',
        'https://ic.wampi.ru/2021/08/19/card-5.png',
        'https://ic.wampi.ru/2021/08/19/card-6.png',
        ]
        url = random.choice(listurl)
    else:
        url = server['upsend_sett']['image_url']

    if ust['type'] == "png":

        response = requests.get(url, stream = True)
        response = Image.open(io.BytesIO(response.content))
        response = response.convert("RGBA")
        img = response.resize((720, 217), Image.ANTIALIAS) # улучшение качества

    if ust['type'] == "gif":

        response = requests.get(url, stream=True)
        response.raw.decode_content = True
        img = Image.open(response.raw)


    mask = Image.new('L', (720, 217))
    bar = Image.new('RGB', (720, 217))

    ImageDraw.Draw(mask).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = 160)
    ImageDraw.Draw(bar).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = (0, 0, 0) )
    bar = bar.filter(ImageFilter.BoxBlur(0.5))
    mask = mask.filter(ImageFilter.BoxBlur(1.5))
    alpha = Image.composite(bar, alpha, mask)

    idraw = ImageDraw.Draw(alpha)
    para = ImageFont.truetype("fonts/20421.ttf", size = 30)
    paga = ImageFont.truetype("fonts/20421.ttf", size = 60)
    pata = ImageFont.truetype("fonts/20421.ttf", size = 50)
    idraw.text((515,70), f"+{str(bal)}\n монет", font = para)

    if len(str(lvl)) == 1:
        idraw.text((530,130), f"{lvl} > {lvl+1}", font = paga)
    elif len(str(lvl)) == 2:
        idraw.text((500,130), f"{lvl} > {lvl+1}", font = paga)
    else:
        idraw.text((500,130), f"{lvl} > {lvl+1}", font = pata)


    try:
        url = str(member.avatar.url)
        response1 = requests.get(url, stream = True)
        response1 = Image.open(io.BytesIO(response1.content))

    except Exception:
        byteImgIO = io.BytesIO()
        url = str(member.avatar.url)[:-9]
        response = requests.get(url, stream = True)
        response.raw.decode_content = True
        response1 = Image.open(response.raw)

    response1 = response1.convert("RGBA")
    response1 = response1.resize((200, 200), Image.ANTIALIAS)
    size = (200, 200)

    im = response1
    im = crop(im, size)
    im.putalpha(prepare_mask(size, 4))

    bg_img = alpha
    fg_img = im
    alpha = trans_paste(fg_img, bg_img, 1.0, (10, 10, 210, 210))


    if ust['type'] == "png":
        img = bl_f(img)

        bg_img = img
        fg_img = alpha
        img = trans_paste(fg_img, bg_img, 1.0)

        image = img
        output = BytesIO()
        image.save(output, 'png')
        image_pix=BytesIO(output.getvalue())

        file = discord.File(fp = image_pix, filename="up_card.png")
        ul = 'png'

    if ust['type'] == "gif":
        fs = []
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")
            frame = frame.resize((720, 217), Image.ANTIALIAS)
            frame = bl_f(frame)

            bg_img = frame
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            b = io.BytesIO()
            frame.save(b, format="GIF",optimize=True, quality=75)
            frame = Image.open(b)
            fs.append(frame)


        fs[0].save('up_card.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=75)

        file = discord.File(fp = "up_card.gif", filename="up_card.gif")
        ul = 'gif'


    up_text = functions.text_replase(server['upsend_sett']['up_message'], message.author)
    if up_text == None:
        up_text = f'<@{message.author.id}>'

    if UpSend == 777777777777777777 or UpSend == True:
        up = message.channel
    else:
        up =  bot.get_channel(UpSend)

    try:

        if server['upsend_sett']['emb_st'] == False:
            await up.send(up_text, file = file)

        if server['upsend_sett']['emb_st'] == True:
            emb = discord.Embed(description = up_text, color= server['embed_color'])
            emb.set_image(url=f"attachment://up_card.{ul}")
            await up.send(file=file, embed = emb)

    except Exception:
        pass


    try:
        os.remove(f'up_card.{ul}')
    except Exception:
        pass



async def lvl(message, server):

    user = functions.user_check(message.author, message.guild)
    expn = 5 * user['lvl']*user['lvl'] + 50 * user['lvl'] + 100
    expi = random.randint(0, server['economy']['lvl_xp'])
    expii = user['xp'] + expi

    functions.user_update(message.author.id, message.guild, "xp", expii)

    if user != None:
        if user['guild'] != None:
            rpg = server['rpg']
            guild = rpg['guild'][f'{user["guild"]}']
            exp = guild['exp'] + random.randint(0, 5)
            guild.update({'exp': exp})
            servers.update_one( {"server": guild.id}, {"$set": {'rpg': rpg}} )
            expnc = 5 * guild['lvl'] * guild['lvl'] + 50 * guild['lvl'] + 100

            if expnc <= exp:
                guild.update({'exp': 0})
                guild.update({'lvl': guild['lvl']+1 })
                servers.update_one( {"server": guild.id}, {"$set": {'rpg': rpg}} )

    if expn <= user['xp']:
        try:
            await lvl_up_image(message, user, server)
        except Exception:
            pass

    return True



async def mod_flud(message, server, met = None):
    #Возвращаем False если всё норм, True если замечено нарушение

    messages = await message.channel.history().flatten()
    l = []

    for mess in messages:
        if mess.author.id == message.author.id:
            if message.content != '':
                l.append(mess)


    if met == None:
        lm = []
        counter = 0
        for i in l:
            if counter != server['mod']['flud_shield']['repetitions']:
                lm.append(i.content)
                counter += 1

        flud_p = 0
        for mes in lm:
            if fuzz.token_sort_ratio(message.content, mes) > 80 or fuzz.ratio(message.content, mes) > 80:
                flud_p += 1


        if flud_p >= server['mod']['flud_shield']['repetitions']:
            return True

        else:
            return False

    else:
        lm = []
        counter = 0
        for i in l:
            if counter != server['mod']['flud_shield']['repetitions']:
                lm.append(i)
                counter += 1

        return lm

def mod_bad_words(message, server):

    allword = ''

    for word in server['mod']['bad_words']['words']:
        for spw in message.content.split():
            allword = allword + spw
            if fuzz.token_sort_ratio(word,allword) > 90:
                return True

            if allword.find(str(word)) != -1:
                return True

            if spw.find(str(word)) != -1:
                return True

    return False

def mod_media(message):
    count = 0
    for attach in message.attachments:
        count += 1

    if count > 0:
        return False
    else:
        return True

async def punishment_mod(message, server, p, reason, shield):

    user = message.author

    if 'ban' in p:
        try:
            await message.author.ban(reason="Auto flud ban")
        except Exception:
            pass

    if 'ban' not in p:

        if 'kick' in p:
            try:
                await message.author.kick(reason= 'Auto flud kick')
            except Exception:
                pass

        if 'kick' not in p:

            if 'warn' in p:
                await functions.warn(await bot.get_context(message), message.author, reason, bot.user)

            if 'role-add' in p:
                if server['mod'][shield]['add-role'] != None:
                    try:
                        await user.add_roles(bot.get_guild(message.guild.id).get_role(server['mod'][shield]['add-role']))
                    except Exception:
                        pass

            if 'role-remove' in p:
                if server['mod'][shield]['roleremove'] != None:
                    try:
                        await user.remove_roles(bot.get_guild(message.guild.id).get_role(server['mod'][shield]['remove-role']))
                    except Exception:
                        pass

    if 'message' in p:
        if server['mod'][shield]['message'] != None:
            try:
                if server['mod'][shield]['mess-type'] == 'emb':
                    emb = discord.Embed(description = server['mod'][shield]['message'], color=0xf03e65)
                    await message.channel.send(embed = emb)
                if server['mod'][shield]['mess-type'] == 'mes':
                    await message.channel.send(server['mod'][shield]['message'])
            except Exception:
                pass

    if 'delete-all' in p:
        ms = await mod_flud(message, server, 'noNone')
        for mess in ms:
            try:
                await mess.delete()
            except Exception:
                pass

    if 'delete' in p:
        if 'delete-all' not in p:
            try:
                await message.delete()
            except Exception:
                pass


@bot.event
async def on_message(message):

    s = settings.find_one({"sid": 1})

    if message.author.bot == True: return
    if message.guild == None:
        emb = discord.Embed(description = "Йоу, перейдите на сервер что бы использовать бота. \n Если у вас нету подходящего сервера, вы можете перейти на сервер поддержки бота > [Клик](https://discord.gg/cFa8K37pBa)", color=0xf03e65)
        await message.channel.send(embed = emb)
        return

    if message.guild.id in s['bl servers']: return

    server = servers.find_one({"server": message.guild.id})

    if server == None:
        functions.insert_server(message.guild)
        server = servers.find_one({"server": message.guild.id})

    #не выполнение команды если человек в мьюте
    try:
        mm = server['mute_members'][f"{message.author.id}"]

        try:
            await message.delete()
        except Exception:
            pass

        return
    except Exception:
        pass

    try:
        if message.content == f'{bot.user.mention}':
            await message.channel.send(f"Гав! Мой префикс `{server['prefix']}`")
    except Exception:
        pass

    if message.author.id in s['black list']: return

    try:
        if message.channel.id in server['mod']['black_channels']: return
    except Exception:
        pass
    try:
        if message.channel.id == server['globalchat']['channel']:
            await global_chat(message, s, server)
            return
    except Exception:
        pass

    # #auto mod
    try:
        if server['mod']['media_channels'] != {} or server['mod']['bad_words'] != {} or server['mod']['flud_shield'] != {} or server['mod']['members_mention'] != {} or server['mod']['roles_mention'] != {}:

            if server['mod']['black_channels'] == [] or message.channel.id not in server['mod']['black_channels']:
                if server['mod']['wlist_members'] == [] or message.author.id not in server['mod']['wlist_members']:

                    list_roles = []
                    for role in message.author.roles: list_roles.append(role.id)
                    if list(set(server['mod']['wlist_roles']) & set(list_roles)) == []:

                        if server['mod']['flud_shield'] != {}:
                            if message.channel.id not in server['mod']['flud_ch_nor']:
                                if await mod_flud(message, server) == True:
                                    try:
                                        await punishment_mod(message, server, server['mod']['flud_shield']['punishment'], 'Auto flud warn', 'flud_shield')
                                    except Exception:
                                        pass

                        if server['mod']['bad_words'] != {}:
                            if mod_bad_words(message, server) == True:
                                try:
                                    await punishment_mod(message, server, server['mod']['bad_words']['punishment'], 'Auto bad-words warn', 'bad_words')
                                except Exception:
                                    pass

                        if server['mod']['media_channels'] != {}:
                            if message.channel.id in server['mod']['media_channels']['channels']:
                                if mod_media(message) == True:
                                    try:
                                        await punishment_mod(message, server, server['mod']['media_channels']['punishment'], 'Auto media-channel warn','media_channels')
                                    except Exception:
                                        pass

                        if server['mod']['members_mention'] != {}:
                            if len(message.raw_mentions) >= server['mod']['members_mention']['repetitions']:
                                try:
                                    await punishment_mod(message, server, server['mod']['members_mention']['punishment'], 'Auto mention warn', 'members_mention')
                                except Exception:
                                    pass

                        if server['mod']['roles_mention'] != {}:
                            if len(message.raw_role_mentions) >= server['mod']['roles_mention']['repetitions']:
                                try:
                                    await punishment_mod(message, server, server['mod']['roles_mention']['punishment'], 'Auto mention warn', 'roles_mention')
                                except Exception:
                                    pass

    except Exception:
        pass


    #выполнение команды
    ctx = await bot.get_context(message)
    try:
        ctx.command = bot.get_command(ctx.invoked_with.lower())
        if ctx.command != None:
            await ctx.trigger_typing()
            try:
                if ctx.command.name not in server['mod']['off_commands']:
                    if functions.cooldown_check(message.author, message.guild, ctx.command.name, 'check') == False:
                        await bot.process_commands(message) # Выполнение команды
                        print(ctx.command.name, 'no_errors')

                        if ctx.command.name in server['mod']['cooldowns'].keys():
                            functions.cooldown_check(message.author, message.guild, ctx.command.name, 'add')

                    else:
                        if server['mod']['cooldowns'][ctx.command.name]['type'] == 'users':

                            if server['mod']['cooldowns'][ctx.command.name]['users'][str(message.author.id)] - int(time.time()) < 0:
                                tt = 0
                            else:
                                tt = int(server['mod']['cooldowns'][ctx.command.name]['users'][str(message.author.id)] - time.time())

                        elif server['mod']['cooldowns'][ctx.command.name]['type'] == 'server':

                            if server['mod']['cooldowns'][ctx.command.name]['server_c'] - int(time.time()) < 0:
                                tt = 0
                            else:
                                tt = int(server['mod']['cooldowns'][ctx.command.name]['server_c'] - time.time())

                        elif server['mod']['cooldowns'][ctx.command.name]['type'] == 'roles':

                            if server['mod']['cooldowns'][ctx.command.name]['role_c'] - int(time.time()) < 0:
                                tt = 0
                            else:
                                tt = int(server['mod']['cooldowns'][ctx.command.name]['role_c'] - time.time())

                        emb = discord.Embed(title = 'Режим ожидания', description = f"Включён режим ожидания, вам осталось ждать {functions.time_end(tt)}", color =server['embed_color'])
                        await message.channel.send(embed = emb)

            except Exception:
                await bot.process_commands(message)
                print(ctx.command.name, 'error')

    except Exception:
        pass

    try:
        if message.channel.id == server['emoji']["emoji_channel"]:
            if server['emoji']["emojis"] != []:
                try:
                    for x in server['emoji']["emojis"]:
                        await message.add_reaction(x)
                except Exception:
                    pass
    except Exception:
        pass

    if functions.user_check(message.author, message.guild, 'dcheck') != False:
        if cooldown(message.author.id, message.guild.id ) == True:
            if len(message.content) >= 5:
                await lvl(message, server)


#============================================конец=================================================================#
bot.run(config.bot_token)
