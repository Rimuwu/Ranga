import nextcord as discord
from nextcord.ext import tasks, commands
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import pprint
from fuzzywuzzy import fuzz
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO


sys.path.append("..")
from functions import functions as funs
import config

client = funs.mongo_c()
db = client.bot
backs = db.bs
servers = db.servers


class clubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage = '[guild_name / guild_tag / guild_id]', description = 'Информация о гильдии', aliases = ['гильдия_инфо', 'guild'])
    async def guild_info(self, ctx, *, name = None):
        user = funs.user_check(ctx.author, ctx.author.guild)
        server = servers.find_one({"server": ctx.guild.id})
        guilds = server['rpg']['guilds']

        user_guild_id = None
        rpg_guild_id = None
        member_in_guild = False
        member = ctx.author

        if name != None:
            try:
                rpg_guild = server['rpg']['guilds'][name]
                rpg_guild_id = name
            except:
                pass

        if rpg_guild_id == None:

            for i in server['rpg']['guilds'].keys():
                g = server['rpg']['guilds'][i]
                if str(member.id) in g['members'].keys():
                    member_in_guild = True
                    user_guild_id = i

        if name == None and member_in_guild == False and rpg_guild_id == None:
            emb = discord.Embed(description = 'Введите `тег / название / id` гильдии!\nТак же вы можете @упоминуть пользователя для получения его гильдии!',color=server['embed_color'])
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return

        elif member_in_guild == True and name == None:
            rpg_guild_id = user_guild_id

        elif name != None and rpg_guild_id == None:

            try:
                rpg_guild = server['rpg']['guilds'][rpg_guild_id]

            except:
                name = "".join(name)
                for i in guilds.keys():
                    i_name = guilds[i]['name']
                    i_tag = guilds[i]['tag']
                    if fuzz.token_sort_ratio(i_name, name) > 80 or fuzz.ratio(i_name, name) > 80 or i_name == name:
                        rpg_guild_id = i
                    elif fuzz.token_sort_ratio(i_tag, name) > 80 or fuzz.ratio(i_tag, name) > 80 or i_tag == name:
                        rpg_guild_id = i

        if rpg_guild_id == None and name != None:
            try:
                try:
                    member_id = int(name[2:-1])
                    print(member_id)
                    member = ctx.guild.get_member(member_id)

                    for i in server['rpg']['guilds'].keys():
                        g = server['rpg']['guilds'][i]
                        if str(member.id) in g['members'].keys():
                            rpg_guild_id = i

                except:
                    member_id = int(name)
                    member = ctx.guild.get_member(member_id)

                    for i in server['rpg']['guilds'].keys():
                        g = server['rpg']['guilds'][i]
                        if str(member.id) in g['members'].keys():
                            rpg_guild_id = i
            except:
                pass

        if rpg_guild_id == None:
            emb = discord.Embed(description = 'Гильдия не была найдена!\nВведите более корректно тег / название / id гильдии!\nТак же вы можете @упоминуть пользователя для получения его гильдии!',color=server['embed_color'])
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:
            rpg_guild = server['rpg']['guilds'][rpg_guild_id]
            expnc = 5 * rpg_guild['lvl'] * rpg_guild['lvl'] + 50 * rpg_guild['lvl'] + 100

            for m in rpg_guild['members'].keys():
                if rpg_guild['members'][m]['role'] == 'owner':
                    guild_owner = m
                    break

            if rpg_guild['main_location'] == None:
                ml = 'Отсутствует'
            else:
                ml = rpg_guild['main_location']

            main_emb = discord.Embed(color=0xf03e65)
            main_emb.add_field(name = '<:recipe:827221967886745600> | Информация', value =
            f"**Создатель**: <@{guild_owner}>\n"
            f"**Участников**: `{len(rpg_guild['members'].keys())}` / `{rpg_guild['max_users']}`\n"
            f"**Создан**: <t:{rpg_guild['created']}> (<t:{rpg_guild['created']}:R>)\n"
            , inline = False)

            if rpg_guild['flag'] != None:
                main_emb.set_author(icon_url = rpg_guild['flag'], name = f" | {rpg_guild['name']} #{rpg_guild['tag']} ID: {rpg_guild_id}")
            else:
                main_emb.set_author( name = f" | {rpg_guild['name']} #{rpg_guild['tag']} ID: {rpg_guild_id}")

            main_emb.add_field(name = '🏰 | Статитстика', value =
            f"**Уровень**: {rpg_guild['lvl']} <:lvl:886876034149011486>\n"
            f"**Опыт**: {rpg_guild['exp']} / {expnc}\n"
            f"**Монет**: {rpg_guild['bank']} <:pokecoin:780356652359745537>\n"
            f"**Штаб**: {ml}\n"
            f"**Захвачено**: {len(rpg_guild['locations'])}"
            , inline = False)

            main_emb.add_field(name = '📰 | Описание:', value = f'{rpg_guild["bio"]}', inline = False)
            if rpg_guild['global_club'] == False:
                main_emb.add_field(name = '🎈 | Доступность: Закрыт', value = f'В гильдию можно вступить только по приглашению админа / создателя!', inline = True)
            if rpg_guild['global_club'] == True:
                if rpg_guild['lvl_enter'] == 0:
                    main_emb.add_field(name = '🎈 | Доступность: Открыт', value = f'Все могут вступить в данную гильдию.', inline = True)
                else:
                    main_emb.add_field(name = '🎈 | Доступность: Открыт', value = f"Минимальный уровень: {rpg_guild['lvl_enter']}\nИли по приглашению создателя / админа гильдии.", inline = True)

            admin_list = []
            rest_members = []

            for mkey in rpg_guild['members'].keys():
                mem = rpg_guild['members'][mkey]

                if mem['role'] == 'admin':
                    admin_list.append({mkey:'admin'})

                elif mem['role'] == 'member':
                    rest_members.append({mkey:'member'})

            members_n = []
            members_n += [{str(guild_owner): 'owner'}]
            members_n += admin_list
            members_n += rest_members

            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            members = list(chunks(members_n, 6))
            emb_members_list = []

            for l_m in members:
                memb = discord.Embed(description = f"**👥 | Участники:**", color=0xf03e65)
                for n in l_m:
                    for m_key in list(n.keys()):
                        # gl_member = server['users'][m_key]
                        mrole = n[m_key]
                        member = ctx.guild.get_member(int(m_key))
                        if mrole == 'owner':
                            memb.add_field(name = f'{member}', value = f'👑 | Роль: Гильдмастер', inline = True)
                        elif mrole == 'admin':
                            memb.add_field(name = f'{member}', value = f'🛡 | Роль: Администратор', inline = True)
                        elif mrole == 'member':
                            memb.add_field(name = f'{member}', value = f'🗡 | Роль: Участник', inline = True)

                emb_members_list.append(memb)

            top_lvl = {"1": {'m': None, 'lvl': 0}, "2": {'m': None, 'lvl': 0}, "3": {'m': None, 'lvl': 0}}
            top_mon = {"1": {'m': None, 'money': 0}, "2": {'m': None, 'money': 0}, "3": {'m': None, 'money': 0}}


            for g_u_id in list(rpg_guild['members'].keys()):
                u = ctx.guild.get_member(int(g_u_id))
                guser = funs.user_check(u, ctx.guild)
                if guser['lvl'] > top_lvl['1']['lvl']:
                    top_lvl['1'] = {'m': u, 'lvl': guser['lvl']}
                elif guser['lvl'] > top_lvl['2']['lvl']:
                    top_lvl['2'] = {'m': u, 'lvl': guser['lvl']}
                elif guser['lvl'] > top_lvl['3']['lvl']:
                    top_lvl['3'] = {'m': u, 'lvl': guser['lvl']}

                if guser['money'] > top_mon['1']['money']:
                    top_mon['1'] = {'m': u, 'money': guser['money']}
                elif guser['money'] > top_mon['2']['money']:
                    top_mon['2'] = {'m': u, 'money': guser['money']}
                elif guser['money'] > top_mon['3']['money']:
                    top_mon['3'] = {'m': u, 'money': guser['money']}

            lvl_text = f"<:gold_s:929729448746549308> 1# {top_lvl['1']['m'].mention}\nУровень: {top_lvl['1']['lvl']}\n"

            if top_lvl['2']['m'] != None:
                lvl_text += f"<:silver_s:929729593286484029> 2# {top_lvl['2']['m'].mention}\nУровень: {top_lvl['2']['lvl']}\n"
            if top_lvl['3']['m'] != None:
                lvl_text += f"<:bronze_s:929729607836520448> 3# {top_lvl['3']['m'].mention}\nУровень: {top_lvl['3']['lvl']}"


            top_emb = discord.Embed(description = f"**📊 | Лидеры гильдии:**", color=0xf03e65)
            top_emb.add_field(name = f"<:lvl:886876034149011486> | Лидеры по уровню", value = lvl_text, inline = True)

            money_text = f"<:gold_s:929729448746549308> 1# {top_mon['1']['m'].mention}\nМонеты: {top_mon['1']['money']}\n"

            if top_mon['2']['m'] != None:
                money_text += f"<:silver_s:929729593286484029> 2# {top_mon['2']['m'].mention}\nМонеты: {top_mon['2']['money']}\n"
            if top_mon['3']['m'] != None:
                money_text += f"<:bronze_s:929729607836520448> 3# {top_mon['3']['m'].mention}\nМонеты: {top_mon['3']['money']}"

            top_emb.add_field(name = f"<:pokecoin:780356652359745537> | Лидеры по монетам", value = money_text, inline = True)


            if rpg_guild['banner_url'] == None:
                url = 'https://cdn.discordapp.com/attachments/932577316649967678/934129438881374280/71509-1542236334.jpg'
            else:
                url = rpg_guild['banner_url']


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
                mask = Image.open('elements/elips_mask.png').convert('L').resize(s, Image.ANTIALIAS)

                output = ImageOps.fit(im, s, centering=(0.5, 0.5))
                output.putalpha(mask)
                return output


            #                                                   задний фон и альфа

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            response = response.convert("RGBA")
            img = response.resize((1100, 400), Image.ANTIALIAS) # улучшение качества


            alpha = Image.open('elements/alpha.png').resize((1100, 400), Image.ANTIALIAS)

            mask = Image.new('L',(1100, 400))
            bar = Image.new('RGB',(1100, 400))

            #                                         панель
            ImageDraw.Draw(mask).polygon(xy=[(0, 0),(700, 0),(300,400),(0,400)], fill = 190)
            ImageDraw.Draw(bar).polygon(xy=[(0, 0),(700, 0),(300,400),(0,400)], fill = (0,0,0,0))


            bar = bar.filter(ImageFilter.BoxBlur(0.5))
            mask = mask.filter(ImageFilter.BoxBlur(1.5))
            alpha = Image.composite(bar, alpha, mask)


            #                                       флаг
            if rpg_guild['flag'] != None:
                sz = 100

                response1 = requests.get(rpg_guild['flag'], stream = True)
                response1 = Image.open(io.BytesIO(response1.content))
                response1 = response1.convert("RGBA")
                response1 = response1.resize((sz, sz), Image.ANTIALIAS)
                im = crop(response1, (sz, sz))

                wh = Image.new(mode = 'RGB', color = 'white', size = (sz+10,sz+10))
                wh = crop(wh, (sz+10,sz+10))

                bg_img = wh
                fg_img = im
                rim = trans_paste(fg_img, bg_img, 1.0, (5, 5, sz+5, sz+5))

                bg_img = alpha
                fg_img = rim
                alpha = trans_paste(fg_img, bg_img, 1.0, (15, 15, 15 + sz+10, 15 + sz+10))


            if rpg_guild['flag'] == None:
                rpg_icon = Image.open(f"elements/icon_rpg.png").resize((130, 130), Image.ANTIALIAS)
                alpha = trans_paste(rpg_icon, alpha, 1.0, (5, 5, 135, 135))


            text_image = Image.open(f"elements/guild_banner.png")
            alpha = trans_paste(text_image, alpha, 1.0)

            #                                  информация
            name = rpg_guild['name']
            tag = rpg_guild['tag']
            coins = rpg_guild['bank']
            lvl = rpg_guild['lvl']
            exp = rpg_guild['exp']
            terr = len(rpg_guild['locations'])

            exp_pr = int(exp / ((5 * lvl * lvl + 50 * lvl + 100) / 100)) #процент опыта

            if len(name) > 25:
                banner_size = 30
                banner_v = 30
            elif len(name) >= 25:
                banner_size = 35
                banner_v = 35
            elif len(name) >= 20:
                banner_size = 42
                banner_v = 30
            else:
                banner_size = 55
                banner_v = 25

            idraw = ImageDraw.Draw(alpha)

            f1 = ImageFont.truetype("fonts/ofont.ru_FloraC.ttf", size = banner_size)
            f1_0 = ImageFont.truetype("fonts/ofont.ru_FloraC.ttf", size = 35)
            f2 = ImageFont.truetype("fonts/BBCT.ttf", size = 40)

            idraw.text((145,banner_v), name, font = f1)
            idraw.text((145,banner_v + 50), f'#{tag}', font = f1_0)
            idraw.text((80,335), "{:,}".format(coins).replace(',', '.'), font = f2)
            idraw.text((80,267), f'Lv: {lvl} | Xp: {exp_pr}%', font = f2)
            idraw.text((80,202), f'Locations: {terr}', font = f2)

            bg_img = img
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            output = BytesIO()
            img.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="guild_banner.png")
            atach = "attachment://guild_banner.png"

            main_emb.set_image(url="attachment://guild_banner.png")
            top_emb.set_image(url="attachment://guild_banner.png")
            for em in emb_members_list:
                em.set_image(url="attachment://guild_banner.png")


            class Dropdown(discord.ui.Select):
                def __init__(self, ctx, msg, options, placeholder, min_values, max_values:int, rem_args):
                    #options.append(discord.SelectOption(label=f''))

                    super().__init__(placeholder=placeholder, min_values=min_values, max_values=min_values, options=options)

                async def callback(self, interaction: discord.Interaction):
                    if ctx.author.id == interaction.user.id:
                        await embed(msg, self.values[0])

                    else:
                        await interaction.response.send_message(f'Жми на свои кнопки!', ephemeral = True)


            class DropdownView(discord.ui.View):
                def __init__(self, ctx, msg, options:list, placeholder:str, min_values:int = 1, max_values:int = 1, timeout: float = 20.0, rem_args:list = []):
                    super().__init__()
                    self.add_item(Dropdown(ctx, msg, options, placeholder, min_values, max_values, rem_args))

                # async def on_error(self, error, item, interaction):
                #     print(error)

            sections = {
            'Участники': emb_members_list,
            'Информация': main_emb,
            'Лидеры': top_emb,
            }

            def op():
                options = []
                options.append(discord.SelectOption(emoji = f'🏰', label = 'Информация'))
                options.append(discord.SelectOption(emoji = f'👥', label = 'Участники'))
                options.append(discord.SelectOption(emoji = f'📊', label = 'Лидеры'))
                return options

            async def embed(msg, sec):
                nonlocal server, ctx, sections
                if sec in ['Информация', 'Участники', 'Лидеры']:
                    emb = sections[sec]

                    if sec == 'Участники':
                        emb_l = emb

                        if len(emb_l) > 1:

                            options = []
                            options.append(discord.SelectOption(label = f'Вернуться', emoji = '🚪'))
                            a = 0
                            for p in emb_l:
                                a += 1
                                options.append(discord.SelectOption(label = f'Страница {a}', emoji = '🧭'))

                            await msg.edit(embed = emb[0], view=DropdownView(ctx, msg, options = options, placeholder = '🧾 | Выберите страницу...', min_values = 1, max_values=1, timeout = 120.0, rem_args = []))
                        else:
                            await msg.edit(embed = emb[0])

                    else:
                        await msg.edit(embed = emb)

                elif sec == 'Вернуться':
                    options = op()
                    await msg.edit(embed = sections['Информация'], view=DropdownView(ctx, msg, options = options, placeholder = '🧾 | Выберите категорию...', min_values = 1, max_values=1, timeout = 20.0, rem_args = []))

                else:
                    n = int(sec[9:]) - 1

                    options = []
                    options.append(discord.SelectOption(label = f'Вернуться', emoji = '🚪'))
                    a = 0
                    for p in sections['Участники']:
                        a += 1
                        options.append(discord.SelectOption(label = f'Страница {a}', emoji = '🧭'))

                    await msg.edit(embed = sections['Участники'][n], view=DropdownView(ctx, msg, options = options, placeholder = '🧾 | Выберите страницу...', min_values = 1, max_values=1, timeout = 120.0, rem_args = []))

            options = op()
            msg = await ctx.send(embed = main_emb, file = file)
            await msg.edit(view=DropdownView(ctx, msg, options = options, placeholder = '🧾 | Выберите категорию...', min_values = 1, max_values=1, timeout = 20.0, rem_args = []))


    # @commands.command(usage = '(tag <= 4 characters) (lvl_enter) (open_status + / -) (name <= 25 characters)', description = 'Создание гильдии.\nСтоимость 5к',aliases = ['создать_гилдию', 'g_create', 'gcreate', 'guildcreate'])
    # async def guild_create(self, ctx, tag = None, lvl_enter:int = 0, open_status = "-", *, name = None):
    #
    #     member = ctx.author
    #     player = funs.user_check(member, member.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #
    #     if player['money'] < 5000:
    #         emb = discord.Embed(description = f'У вас не достаточно монет для создания гильдии! Сейчас у вас {player["money"]}, а требуется 5к',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #
    #     if tag is None:
    #         emb = discord.Embed(description = 'Введите тег гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif len(tag) > 4:
    #         emb = discord.Embed(description = 'Тег гильдии слишком длиный! (максимум 4 символа) ', color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif lvl_enter < 0:
    #         emb = discord.Embed(description = 'Уровень входа не может быть меньше 0!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif open_status not in ['+', '-']:
    #         emb = discord.Embed(description = 'Укажите + если хотите сдлать гильдию открытой, - если доступной только по приглашению. ',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif name is None:
    #         emb = discord.Embed(description = 'Введите название гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif len(name) > 25:
    #         emb = discord.Embed(description = 'Имя гильдии слишком длиное! (максимум 25 символов) ',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #         if open_status == '+':
    #             status = True
    #         else:
    #             status = False
    #
    #         name_u = False
    #         tag_u = False
    #         member_in_guild = False
    #         for i in server['rpg']['guilds'].keys():
    #             g = server['rpg']['guilds'][i]
    #             if g['name'] == name:
    #                 name_u = True
    #             if g['tag'] == tag:
    #                 tag_u = True
    #             if str(ctx.author.id) in g['members'].keys():
    #                 member_in_guild = True
    #
    #         if name_u == True:
    #             emb = discord.Embed(description = 'Гильдия с данным названием уже существует!',color=server['embed_color'])
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #         elif tag_u == True:
    #             emb = discord.Embed(description = 'Гильдия с данным тегом уже существует!',color=server['embed_color'])
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #         elif member_in_guild == True:
    #             emb = discord.Embed(description = f'Вы уже в гильдии!',color=server['embed_color'])
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #         else:
    #             emb = discord.Embed(description = 'Вы успешно создали гильдию!',color=server['embed_color'])
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #             if len(server['rpg']['guilds']) == 0:
    #                 g_id = "1"
    #             else:
    #                 simpl_list = []
    #                 for i in server['rpg']['guilds'].keys():
    #                     simpl_list.append(int(i))
    #
    #                 g_id = str(max(simpl_list)+1)
    #
    #
    #             server['rpg']['guilds'][g_id] = { "name": name, 'tag': tag, "bio": 'Пусто', "flag": None, "lvl": 1, "exp": 0, "created": int(time.time()), "members": {str(ctx.author.id): {"role": 'owner'}}, 'global_club': status, 'lvl_enter': lvl_enter, 'max_users': 50, 'bank': 0, 'inv': [], 'main_location': None, 'locations': [], 'banner_url': None }
    #
    #             servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': server['rpg']}} )
    #             funs.user_update(member.id, ctx.guild, met, user['money'] - 5000)
    #
    #
    # @commands.command(usage = '(url)', description = 'Установка баннера гильдии. Стоимость 1к\nРазмер изображения должен быть 1100х400', aliases = ['баннер_гильдии', 'gbanner'])
    # async def guild_banner(self, ctx, link = None):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner', 'admin']:
    #         emb = discord.Embed(description = 'Только гильдмастер / админ может поменять баннер гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #
    #     if link is None:
    #         emb = discord.Embed(description = 'Укажите ссылку на баннер для гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     else:
    #
    #         try:
    #             response = requests.get(link, stream = True)
    #             response = Image.open(io.BytesIO(response.content))
    #         except:
    #             emb = discord.Embed(description = 'Требовалось указать ссылку на изображение 1100 на 400 пикселей!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #
    #         if response.size != (1100, 400):
    #             emb = discord.Embed(description = 'Требовалось указать ссылку на изображение 1100 на 400 пикселей!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #
    #         if user['money'] > 999:
    #
    #             emb = discord.Embed(description = 'Вы поменяли баннер гильдии!', color=0xf03e65)
    #             emb.set_image(url = link)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #             user['money'] -= 1000
    #             funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - 1000)
    #
    #             server['rpg']['guilds'][rpg_guild_id]['banner_url'] = link
    #             servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': server['rpg']}} )
    #
    #
    #         else:
    #             emb = discord.Embed(description = 'Недостаточно монет (требуется 1.000 монет)!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    # @commands.command(usage = '(url)', description = 'Установка герба гильдии. Стоимость 1к', aliases = ['gflag'])
    # async def guild_flag(self, ctx, link = None):
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner', 'admin']:
    #         emb = discord.Embed(description = 'Только гильдмастер / админ может поменять герб гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #
    #     if link is None:
    #         emb = discord.Embed(description = 'Укажите ссылку на герб гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     else:
    #
    #         try:
    #             response = requests.get(link, stream = True)
    #             response = Image.open(io.BytesIO(response.content))
    #         except:
    #             emb = discord.Embed(description = 'Требовалось указать ссылку на изображение!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #
    #         if user['money'] > 999:
    #
    #             emb = discord.Embed(description = 'Вы поменяли герб гильдии!', color=0xf03e65)
    #             emb.set_image(url = link)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #             user['money'] -= 1000
    #             funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - 1000)
    #
    #             server['rpg']['guilds'][rpg_guild_id]['flag'] = link
    #             servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': server['rpg']}} )
    #
    #
    #         else:
    #             emb = discord.Embed(description = 'Недостаточно монет (требуется 1.000 монет)!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #
    # @commands.command(usage = '(bio)', description = 'Установка информации о гильдии.', aliases = ['био_гильдии','gbio'])
    # async def guild_bio(self, ctx, *, bio = None):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner', 'admin']:
    #         emb = discord.Embed(description = 'Только гильдмастер / админ может поменять описание гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #
    #         if bio is None:
    #             emb = discord.Embed(description = 'Укажите описание!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #         elif len(bio) > 500:
    #             emb = discord.Embed(description = 'Слишком много символов (макс: 500)', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #
    #
    #         else:
    #             emb = discord.Embed(description = f'Вы поменяли описание вашей гильдии на: {bio}', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #             server['rpg']['guilds'][rpg_guild_id]['bio'] = bio
    #             servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': server['rpg']}} )
    #
    #
    # @commands.command(usage = '(@member)', description = 'Приглашение в гильдию.', aliases = ['пригласить','ginvite'])
    # async def guild_invite(self, ctx, member: discord.Member = None):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #     member_in_guild = False
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner', 'admin']:
    #         emb = discord.Embed(description = 'Только гильдмастер / админ может приглашать в гильдию!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #         if member is None:
    #             emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         for i in server['rpg']['guilds'].keys():
    #             g = server['rpg']['guilds'][i]
    #             if str(member.id) in g['members'].keys():
    #                 member_in_guild = True
    #
    #
    #         if member_in_guild == False:
    #             if len(guild['members']) < guild['max_users']:
    #
    #                 emb = discord.Embed(description = f'**{member.mention}**, вы были приглашены в гильдию **{guild["name"]}**\nХотите принять приглашение?\nПриглашение истекает: <t:{int(time.time()+600)}:R>', color=0xf03e65)
    #                 emb.set_author(icon_url = guild['flag'], name = guild['name'])
    #
    #                 message = await ctx.send(embed = emb)
    #
    #                 react = await funs.reactions_check(self.bot, ['✅', '❌'], member, message, True, 600)
    #
    #                 if str(react) == '✅':
    #
    #                     emb = discord.Embed(description = f'**{member.mention}** принял(а) приглашение в гильдию!', color=0xf03e65)
    #                     emb.set_author(icon_url = guild['flag'], name = guild['name'])
    #                     await message.edit(embed = emb)
    #
    #                     server = servers.find_one({"server": ctx.guild.id})
    #                     guild = server['rpg']['guilds'][rpg_guild_id]
    #                     guild['members'][str(member.id)] = {'role': 'member'}
    #                     r = server['rpg']
    #                     r['guilds'][rpg_guild_id] = guild
    #                     servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': r }} )
    #
    #                 elif str(react) == '❌':
    #
    #                     emb = discord.Embed(description = f'**{member.mention}** отказался от приглашения!', color=0xf03e65)
    #                     emb.set_author(icon_url = guild['flag'], name = guild['name'])
    #                     await message.edit(embed = emb)
    #
    #                 else:
    #                     emb = discord.Embed(description = f'**{member.mention}** не ответил(а) на приглашение!', color=0xf03e65)
    #                     emb.set_author(icon_url = guild['flag'], name = guild['name'])
    #                     await message.edit(embed = emb)
    #
    #             else:
    #                 emb = discord.Embed(description = 'В гильдии максимальное колличество пользователей!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = 'Пользователь уже в гильдии!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #
    # @commands.command(usage = '(@member)', description = 'Передача прав на гильдию.', aliases = ['передать_создателя','g_owner'])
    # async def guild_owner(self, ctx, member: discord.Member = None):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #     member_guild = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner']:
    #         emb = discord.Embed(description = 'Только гильд-мастер может передать права на гильдию!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #         if member is None:
    #             emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         for i in server['rpg']['guilds'].keys():
    #             g = server['rpg']['guilds'][i]
    #             if str(member.id) in g['members'].keys():
    #                 member_guild = i
    #
    #
    #         if member_guild != rpg_guild_id:
    #             emb = discord.Embed(description = 'Пользователь не в вашей гильдии!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         elif member == ctx.author:
    #             emb = discord.Embed(description = 'Нельзя передать права на гильдию самому себе!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #         else:
    #
    #             emb = discord.Embed(description = f'**{member.mention}** стал гильд-мастером!', color=0xf03e65)
    #             emb.set_author(icon_url = guild['flag'], name = guild['name'])
    #             await ctx.send(embed = emb)
    #             server = servers.find_one({"server": ctx.guild.id})
    #
    #             guild = server['rpg']['guilds'][rpg_guild_id]
    #             guild['members'][str(member.id)] = {'role': 'owner'}
    #             guild['members'][str(ctx.author.id)] = {'role': 'admin'}
    #             r = server['rpg']
    #             r['guilds'][rpg_guild_id] = guild
    #             servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': r }} )
    #
    # @commands.command(usage = '-', description = 'Покинулть гильдию.', aliases = ['покинуть_гильдию', 'gleave'])
    # async def guild_leave(self, ctx):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #
    #     if guild['members'][str(ctx.author.id)]['role'] != 'owner':
    #
    #         emb = discord.Embed(description = f"Вы покинули гильдию {guild['name']}!", color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #         guild['members'].pop(str(ctx.author.id))
    #         r = server['rpg']
    #         r['guilds'][rpg_guild_id] = guild
    #         servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': r }} )
    #
    #     else:
    #         emb = discord.Embed(description = 'Гильд-мастер не может покинуть гильдию!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    # @commands.command(usage = '(@member)', description = 'Кикнуть пользователя из гильдии.', aliases = ['пнуть_из_гильдии', 'gkick'])
    # async def guild_kick(self, ctx, member: discord.Member = None):
    #
    #     user = funs.user_check(ctx.author, ctx.author.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #     rpg_guild_id = None
    #     member_guild = None
    #
    #     for i in server['rpg']['guilds'].keys():
    #         g = server['rpg']['guilds'][i]
    #         if str(ctx.author.id) in g['members'].keys():
    #             rpg_guild_id = i
    #
    #     if rpg_guild_id == None:
    #         emb = discord.Embed(description = 'Вы не в гильдии!',color=server['embed_color'])
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     guild = server['rpg']['guilds'][rpg_guild_id]
    #
    #     if guild['members'][str(ctx.author.id)]['role'] not in ['owner', 'admin']:
    #         emb = discord.Embed(description = 'Только гильд-мастер / админ может пнуть из гильдии!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #         if member is None:
    #             emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         for i in server['rpg']['guilds'].keys():
    #             g = server['rpg']['guilds'][i]
    #             if str(member.id) in g['members'].keys():
    #                 member_guild = i
    #
    #         if member_guild != rpg_guild_id:
    #             emb = discord.Embed(description = 'Пользователь не в вашей гильдии!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         if guild['members'][str(ctx.author.id)]['role'] != 'owner' or guild['members'][str(member.id)]['role'] in ['owner', 'admin']:
    #             emb = discord.Embed(description = 'Вы можете кикнуть только ниже себя по должности!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         elif member == ctx.author:
    #             emb = discord.Embed(description = 'Невозможно кикнуть самого себя!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #             return
    #
    #         emb = discord.Embed(description = f"Вы кикнули {member.mention} из гильдии!", color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #         guild['members'].pop(str(member.id))
    #         r = server['rpg']
    #         r['guilds'][rpg_guild_id] = guild
    #         servers.update_one( {"server": ctx.guild.id}, {"$set": {'rpg': r }} )


    # @commands.command(usage = '(new_name)', description = 'Изменить название клуба. Стимость 2к', aliases = ['переименовать_клуб'])
    # async def club_rename(self, ctx, *, name = None):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #     guild = db.clubs.find_one({"name": user['guild']})
    #
    #     if name is None:
    #         emb = discord.Embed(description = 'Введите название клуба!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif len(name) > 25:
    #         emb = discord.Embed(description = 'Имя клуба слишком длиное!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #
    #         if user['guild'] == None:
    #             emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #         else:
    #             if guild['owner'] != ctx.author.id:
    #                 emb = discord.Embed(description = 'Только глава может изменить имя клана!', color=0xf03e65)
    #                 emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                 await ctx.send(embed = emb)
    #
    #             else:
    #                 if db.clubs.count_documents({"name": name}):
    #                     emb = discord.Embed(description = 'Такой клуб уже существует!', color=0xf03e65)
    #                     emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                     await ctx.send(embed = emb)
    #                 else:
    #                     result = user['money']
    #                     if result > 1999:
    #                         emb = discord.Embed(description = f'Вы изменили имя клуба на **{name}**', color=0xf03e65)
    #                         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                         await ctx.send(embed = emb)
    #
    #                         names = guild['name']
    #                         members = guild['members']
    #                         db.clubs.update_one({"name": names}, {"$set": {"name": name}})
    #
    #                         for i in members:
    #                             users.update_one({'userid': i}, {'$set': {'guild': name}})
    #
    #                         newcash2 = user['money'] - 2000
    #                         users.update_one({"userid": ctx.author.id}, {"$set": {"money": newcash2}})
    #
    #                     else:
    #                         emb = discord.Embed(description = 'Недостаточно монет (требуется 2.000 монет)!', color=0xf03e65)
    #                         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                         await ctx.send(embed = emb)
    #
    # @commands.command(usage = '(new_tag <= 4 characters)', description = 'Изменение тэга клуба.', aliases = ['сменить_тег_клуба'])
    # async def tag_rename(self, ctx, *, tag = None):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #     guild = db.clubs.find_one({"name": user['guild']})
    #
    #     if tag is None:
    #         emb = discord.Embed(description = 'Введите название клуба!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     elif len(tag) > 4:
    #         emb = discord.Embed(description = 'Имя клуба слишком длиное!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #     else:
    #
    #         if user['guild'] == None:
    #             emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #         else:
    #             if guild['owner'] != ctx.author.id:
    #                 emb = discord.Embed(description = 'Только глава может изменить тег!', color=0xf03e65)
    #                 emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                 await ctx.send(embed = emb)
    #
    #             else:
    #                 if db.clubs.count_documents({"tag": tag}):
    #                     emb = discord.Embed(description = 'Такой тег уже существует!', color=0xf03e65)
    #                     emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                     await ctx.send(embed = emb)
    #                 else:
    #                     result = user['money']
    #                     if result > 3999:
    #                         emb = discord.Embed(description = f'Вы изменили тег на **{tag}**', color=0xf03e65)
    #                         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                         await ctx.send(embed = emb)
    #
    #                         db.clubs.update_one({"name": guild['name']}, {"$set": {"tag": tag}})
    #
    #
    #                         users.update_one({"userid": ctx.author.id}, {"$set": {"money": user['money'] - 400}})
    #
    #                     else:
    #                         emb = discord.Embed(description = 'Недостаточно монет (требуется 4.000)!', color=0xf03e65)
    #                         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #                         await ctx.send(embed = emb)
    #
    # @commands.command(usage = '-', description = 'Удаление своего клуба.', aliases = ['удалить_клуб'])
    # async def club_delete(self, ctx):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #     guild = db.clubs.find_one({"name": user['guild']})
    #
    #     if user['guild'] == None:
    #         emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #
    #
    #     else:
    #         if guild['owner'] != ctx.author.id:
    #
    #             emb = discord.Embed(description = 'Только глава может удалить клуб!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #         else:
    #             emb = discord.Embed(description = 'Вы успешно удалили клуб!', color=0xf03e65)
    #             emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #             await ctx.send(embed = emb)
    #
    #             name = guild['name']
    #             members = guild['members']
    #
    #             for i in members:
    #                 users.update_one({'userid': i}, {'$set': {'guild': None}})
    #
    #
    #             db.clubs.delete_one({"name": name})
    #
    #
    #
    #
    # @commands.command(usage = '(@member)', description = 'Назначение админа клуба.', aliases = ['добавить_админа_клуба'])
    # async def club_admin_add(self, ctx, member: discord.Member = None):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     mem = users.find_one({"userid": member.id})
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #     if member is None:
    #         emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if guild['owner'] == ctx.author.id:
    #             if mem['guild'] == user['guild']:
    #                 ad = guild['admins']
    #                 ad.append(member.id)
    #                 db.clubs.update_one({'name': user['guild']}, {'$set': {'admins': ad}})
    #                 emb = discord.Embed(description = f'Теперь <@{member.id}> админ в вашем клубе!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #             else:
    #                 emb = discord.Embed(description = 'Пользователь не в вашем клубе!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = 'Только глава может назначать админов клуба!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(aliases = ['club_admin_delete', "удалить_админа_клуба"], usage = '(@member)', description = 'Удаление админа клуба.')
    # async def club_admin_remove(self, ctx, member: discord.Member = None):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     mem = users.find_one({"userid": member.id})
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #     if member is None:
    #         emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if guild['owner'] == ctx.author.id:
    #             if mem['guild'] == user['guild']:
    #                 ad = guild['admins']
    #                 ad.remove(member.id)
    #
    #                 db.clubs.update_one({'name': user['guild']}, {'$set': {'admins': ad}})
    #                 emb = discord.Embed(description = f'Вы сняли <@{member.id}> с поста админа!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #             else:
    #                 emb = discord.Embed(description = 'Пользователь не в вашем клубе!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = 'Только глава может назначать админов клуба!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(usage = '-', description = 'Изменение статуса клуба.', aliases = ['статус_клуба'])
    # async def club_status(self, ctx):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #     reaction = 'a'
    #
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
    #
    #             if guild['global_club'] == False:
    #                 t1 = "закрытого"
    #                 t2 = "открытый"
    #                 t3 = True
    #             else:
    #                 t1 = "открытого"
    #                 t2 = "закрытый"
    #                 t3 = False
    #
    #
    #             solutions = ['✒', '❌']
    #             emb1 = discord.Embed(title = f'Смена статуса клуба',
    #             description = f'Нажмите на `✒` что бы сменить статус клуба с `{t1}` на `{t2}`', color=0xf03e65)
    #
    #             emb2 = discord.Embed(title = f'Статус клуба изменён',
    #             description = f'Статус клуба теперь `{t2}`', color=0xf03e65)
    #
    #
    #
    #             msg = await ctx.send(embed = emb1)
    #
    #             def check( reaction, user):
    #                 nonlocal msg
    #                 return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)
    #
    #             async def rr():
    #                 nonlocal reaction
    #                 if str(reaction.emoji) == '✒':
    #                     await msg.remove_reaction('✒', ctx.author)
    #                     await msg.edit(embed = emb2)
    #                     db.clubs.update_one({'name': user['guild']}, {'$set': {'global_club': t3}})
    #                     await msg.clear_reactions()
    #                     pass
    #
    #                 elif str(reaction.emoji) == '❌':
    #                     await msg.clear_reactions()
    #
    #             async def reackt():
    #                 nonlocal reaction
    #                 try:
    #                     reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
    #                 except asyncio.TimeoutError:
    #                     await msg.clear_reactions()
    #                 else:
    #                     await rr()
    #
    #
    #             for x in solutions:
    #                 await msg.add_reaction(x)
    #
    #             await reackt()
    #
    #         else:
    #             emb = discord.Embed(description = 'Только глава/админ может менять статус клуба!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(usage = '(lvl)', description = 'Изменение уровня входа.', aliases = ['уровень_входа'])
    # async def club_lvl_enter(self, ctx, lvl:int = 0):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
    #             if lvl >= 0 and lvl < 999:
    #                 emb = discord.Embed(description = f'Вы поменяли уровень вступления в клуб на {lvl}', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #                 db.clubs.update_one({'name': user['guild']}, {'$set': {'lvl_enter': lvl}})
    #
    #             else:
    #                 emb = discord.Embed(description = 'Можно указать уровень от 0 до 999!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = 'Только глава/админ может менять уровень вступления в клуб!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(usage = '(name)', description = 'Вступить в клую.', aliases = ['вступить'])
    # async def club_enter(self, ctx, *, name = None):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #     if name is None:
    #         emb = discord.Embed(description = 'Укажите клуб!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         return
    #
    #
    #     if user['guild'] == None:
    #         guild = db.clubs.find_one({"name": name})
    #         if guild['global_club'] == False:
    #             await ctx.send("Данный клуб закрытый")
    #             return
    #         if guild != None:
    #             if len(guild['members']) < guild['max_users']:
    #                 if guild['lvl_enter'] <= user['lvl']:
    #                     emb = discord.Embed(description = f'Вы успешно вступили в клуб {guild["name"]}', color=0xf03e65)
    #                     emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                     await ctx.send(embed = emb)
    #
    #                     mem = guild['members']
    #                     mem.append(ctx.author.id)
    #
    #                     db.clubs.update_one({'name': name}, {'$set': {'members': mem}})
    #                     users.update_one({'userid': ctx.author.id}, {'$set': {'guild': name}})
    #
    #                 else:
    #                     emb = discord.Embed(description = 'Ваш уровень меньше чем уровень для вступления в этот клуб!', color=0xf03e65)
    #                     emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                     await ctx.send(embed = emb)
    #             else:
    #                 emb = discord.Embed(description = 'В клубе максимальное колличество пользователей!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = f'Клуба по имени {name} не найден', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы уже состоите в клубе!', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(aliases = ['club_dep', 'пополнить_банк'], usage = '(amout)', description = 'Внести сумму в банк клуба.')
    # async def club_deposit(self,ctx, amout:int):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     kk = self.bot.get_emoji(778533802342875136)
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if user['money'] >= amout and amout > 0:
    #             if user['Nitro'] == False:
    #                 am = amout - amout / 100 * 2
    #             else:
    #                 am = amout
    #
    #             emb = discord.Embed(description = f'Вы положили в банк клуба {am}', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #
    #             users.update_one({'userid':ctx.author.id}, {'$inc':{"money": -amout}})
    #             db.clubs.update_one({'name': user['guild']}, {'$inc':{"bank": round(am)}})
    #
    #         else:
    #             emb = discord.Embed(description = f'У вас не достаточно {kk}монет или число меньше 0!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #
    # @commands.command(usage = '(amout)', description = 'Снять депозит с банка клуба.', aliases = ['снять'])
    # async def club_with(self,ctx, amout:int):
    #
    #
    #     if users.find_one({"userid": ctx.author.id}) == None:
    #         await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
    #         return
    #
    #     kk = self.bot.get_emoji(778533802342875136)
    #     user = users.find_one({"userid": ctx.author.id})
    #
    #     if user['guild'] != None:
    #         guild = db.clubs.find_one({"name": user['guild']})
    #         if guild['bank'] >= amout and amout > 0:
    #             if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
    #
    #                 emb = discord.Embed(description = f'Вы взяли из банка клуба {amout}', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #
    #                 users.update_one({'userid':ctx.author.id}, {'$inc':{"money": amout}})
    #                 db.clubs.update_one({'name': user['guild']}, {'$inc':{"bank": -amout}})
    #
    #             else:
    #                 emb = discord.Embed(description = f'Только глава/админ может взять {kk}монетки из банка клуба!', color=0xf03e65)
    #                 emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #                 await ctx.send(embed = emb)
    #         else:
    #             emb = discord.Embed(description = 'В банке клуба нет такой суммы или число меньше 0!', color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
    #             await ctx.send(embed = emb)
    #     else:
    #         emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
    #         emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
    #         await ctx.send(embed = emb)
    #         await ctx.message.delete()
    #



def setup(bot):
    bot.add_cog(clubs(bot))
