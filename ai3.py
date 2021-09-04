from nextcord.ext import commands
import config
bot = commands.Bot(command_prefix='$')

@bot.command()
async def ping(ctx):
    await ctx.reply('Pong!')

bot.run(config.bot_token)
