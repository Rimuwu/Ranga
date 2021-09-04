import nextcord as discord
from nextcord.ext import commands
import config
import time

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    global start_time

    channel = bot.get_channel(813056001229324308)
    ping = bot.latency
    ping_emoji = "🟩🔳🔳🔳🔳"

    ping_list = [
        {"ping": 0.10000000000000000, "emoji": "🟧🟩🔳🔳🔳"},
        {"ping": 0.15000000000000000, "emoji": "🟥🟧🟩🔳🔳"},
        {"ping": 0.20000000000000000, "emoji": "🟥🟥🟧🟩🔳"},
        {"ping": 0.25000000000000000, "emoji": "🟥🟥🟥🟧🟩"},
        {"ping": 0.30000000000000000, "emoji": "🟥🟥🟥🟥🟧"},
        {"ping": 0.35000000000000000, "emoji": "🟥🟥🟥🟥🟥"}]

    for ping_one in ping_list:
        if ping > ping_one["ping"]:
            ping_emoji = ping_one["emoji"]
            break

    time2 = time.time()
    try:
        await channel.send(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}\n{ping_emoji} `{ping * 1000:.0f}ms`\nВремя на запуск: {functions.time_end(time2 - start_time)}")
        print(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)} - Время на запуск: {functions.time_end(time2 - start_time)}")
    except Exception:
        await channel.send(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}\n{ping_emoji} `{ping * 1000:.0f}ms`")
        print(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}")

@bot.command()
async def ping(ctx):
    await ctx.reply('Pong!')

bot.run(config.bot_token)
