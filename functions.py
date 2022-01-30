import nextcord as discord
from nextcord.utils import utcnow
import math
import time
from datetime import datetime, timedelta
import pprint
import pymongo
import asyncio

import config


client = pymongo.MongoClient(config.cluster_token)
db = client.bot

backs = db.bs
servers = db.servers
settings = db.settings

class functions:

    @staticmethod
    def time_end(seconds:int, mini = False):

        def ending_w(word, number:str, mini):
            if int(number) not in [11,12,13,14,15]:
                ord = int(str(number)[int(len(str(number))) - 1:])
            else:
                ord = int(number)

            if word == 'секунда':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'секунды'
                    elif ord > 4 or ord == 0:
                        newword = 'секунд'
                else:
                    newword = 's'

            elif word == 'минута':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'минуты'
                    elif ord > 4 or ord == 0:
                        newword = 'минут'
                else:
                    newword = 'm'

            elif word == 'час':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'часа'
                    elif ord > 4 or ord == 0:
                        newword = 'часов'
                else:
                    newword = 'h'

            elif word == 'день':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'дня'
                    elif ord > 4 or ord == 0:
                        newword = 'дней'
                else:
                    newword = 'd'

            elif word == 'неделя':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'недели'
                    elif ord > 4 or ord == 0:
                        newword = 'недель'
                else:
                    newword = 'w'

            elif word == 'месяц':
                if mini != True:
                    if ord == 1:
                        newword = word
                    elif ord in [2,3,4]:
                        newword = 'месяца'
                    elif ord > 4 or ord == 0:
                        newword = 'месяцев'
                else:
                    newword = 'M'

            return newword


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

        if mm < 10: mm = f"0{mm}"
        if w < 10: w = f"0{w}"
        if d < 10: d = f"0{d}"
        if h < 10: h = f"0{h}"
        if m < 10: m = f"0{m}"
        if s < 10: s = f"0{s}"

        if m == '00' and h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{s} {ending_w('секунда',s,mini)}"
        elif h == '00' and d == '00' and w == '00' and mm == '00':
            return f"{m} {ending_w('минута',m,mini)}, {s} {ending_w('секунда',s,mini)}"
        elif d == '00' and w == '00' and mm == '00':
            return f"{h} {ending_w('час',h,mini)}, {m} {ending_w('минута',m,mini)}, {s} {ending_w('секунда',s,mini)}"
        elif w == '00' and mm == '00':
            return f"{d} {ending_w('день',d,mini)}, {h} {ending_w('час',h,mini)}, {m} {ending_w('минута',m,mini)}, {s} {ending_w('секунда',s,mini)}"
        elif mm == '00':
            return f"{w} {ending_w('неделя',w,mini)}, {d} {ending_w('день',d,mini)}, {h} {ending_w('час',h,mini)}, {m} {ending_w('минута',m,mini)}, {s} {ending_w('секунда',s,mini)}"
        else:
            return  f"{mm} {ending_w('месяц',mm,mini)}, {w} {ending_w('неделя',w,mini)}, {d} {ending_w('день',d,mini)}, {h} {ending_w('час',h,mini)}, {m} {ending_w('минута',m,mini)}, {s} {ending_w('секунда',s,mini)}"

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

                if cc['time'] == 0:
                    yday = time.localtime(time.time() + 86400)
                    start = time.struct_time((yday.tm_year, yday.tm_mon, yday.tm_mday, 0, 0, 0, 0, 0, yday.tm_isdst))
                    time_end = int(f"{time.mktime(start):.0f}")
                    cl[str(command)]['users'].update({str(user.id): int(time_end) })
                else:
                    cl[str(command)]['users'].update({str(user.id): int(time.time() + cc['time']) })

            elif cc['type'] == 'server':

                if cc['time'] == 0:
                    yday = time.localtime(time.time() + 86400)
                    start = time.struct_time((yday.tm_year, yday.tm_mon, yday.tm_mday, 0, 0, 0, 0, 0, yday.tm_isdst))
                    time_end = int(f"{time.mktime(start):.0f}")
                    cl[str(command)].update({'server_c': int(time_end) })
                else:
                    cl[str(command)].update({'server_c': int(time.time() + cc['time']) })

            elif cc['type'] == 'roles':

                if cc['time'] == 0:
                    yday = time.localtime(time.time() + 86400)
                    start = time.struct_time((yday.tm_year, yday.tm_mon, yday.tm_mday, 0, 0, 0, 0, 0, yday.tm_isdst))
                    time_end = int(f"{time.mktime(start):.0f}")
                    cl[str(command)].update({'role_c': time_end })
                else:
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
                    'part_channels': [],

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

        if reason == None:
            reason = 'Не указана'

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
            except:
                pass

            a = server['mute_members']
            a.update({str(user.id): time.time() + punishment['time'] })
            servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
            ttt = functions.time_end(punishment['time'])
            wtext = f'Мьют: `{ttt}`'

            try:
                await user.edit(timeout=utcnow() + timedelta(seconds = punishment['time']))
            except:
                pass


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
    async def reactions_check(bot, solutions: list, member: discord.Member, msg: discord.Message, clear:bool = False, timeout:float = 30.0):

        def check(reaction, user):
            nonlocal msg
            return user.id == member.id and str(reaction.emoji) in solutions and reaction.message.id == msg.id

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

        def list_counter(list):
            ld = {}
            for i in list:
                if i not in ld.keys():
                    ld[i] = 1
                elif i in ld.keys():
                    ld[i] += 1
            list = []
            for el in ld.keys():
                list.append(f'{el} x{ld[el]}')

            return list



        server = servers.find_one({'server': guild_id})

        ni = {}
        ni['name'] = item['name']
        ni['image'] = item['image']

        try:
            ni['emoji'] = item['emoji']
        except:
            ni['emoji'] = "🏮"

        if ni['emoji'] == None:
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
            ni['act_title'] = f'Выпадаемые предметы:\n`{", ".join(list_counter(server["items"][str(x)]["name"] for x in item["act"]))}`'

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


            ni['act_title'] = f"Требуемые предметы:\n`{', '.join(list_counter(c_i))}`\n"
            if ni_i != []:
                ni['act_title'] += f'Предметы которые не будут удалены:\n`{", ".join(list_counter(ni_i))}`\n'

            ni['act_title'] += f'Создаваемыве предметы:\n`{", ".join(list_counter(ct_i))}`\n'
            if item['uses'] == 0:
                ni['act_title'] += 'Количество использований: Бесконечно'
            else:
                ni['act_title'] += f'Количество использований: {item["uses"]}'


        elif item['type'] == 'role':
            ni['type'] = '<:icons8pokeball96:779718625459437608> | Роль'
            if item['style'] == f'add':
                ni['act_title'] = f"Добавляет вам <@{item['act']}>"
            elif item['style'] == f'remore':
                ni['act_title'] = f"Удаляет у вас <@{item['act']}>"

        elif item['type'] == 'prop':
            ni['type'] = '📦 | Проп'
            ni['act_title'] = 'Является неиграбельным предметом'

        return ni
