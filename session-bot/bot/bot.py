import discord
import logging

from discord.ext import commands
from .schedule import cal

from ..util import config
from ..util.log import fatal_error

from .utils import add_reactions

from .schedule.SessionCog import SessionCog

bot = commands.Bot(command_prefix=config.config['discord']['command_prefix'])
logger = logging.getLogger('session-bot')
COLOUR = discord.Color(int(config.config['style']['colour'], 0))
IMG_URL = config.config['style']['image_url']

interval = int(config.config['discord']['update_interval'])
print(f"interval={interval}")


def main():
    global events_channel_id, guild_id, role_ids
    try:
        token = config.config['discord']['token']
        events_channel_id = int(config.config['discord']['announcement_channel'])
        guild_id = int(config.config['discord']['guild_id'])
        role_ids = list(map(lambda x: int(x), config.config['discord']['roles']))
        if not token:
            fatal_error(f"msg=\"Token was missing!\"")
    except Exception as e:
        fatal_error(f"msg=\"error parsing environment variables\", error=\"{e}\"")
        return
    bot.run(token)

@bot.event
async def on_ready():
    roles = []
    for role_id in role_ids:
        roles.append(bot.get_guild(guild_id).get_role(role_id))
    bot.add_cog(SessionCog(bot=bot, interval=interval, colour=COLOUR, img_url=IMG_URL, roles=roles))
    logger.info('Bot Ready!')


@bot.command(description="Displays next event")
async def next_session(ctx):
    session = cal.get_next_session()
    logger.info("Sending next session via command")
    if session:
        embed = discord.Embed(title=session.title,
                              description=f'Starting at {str(session.start.strftime("%H:%M GMT on %B %d"))}',
                              url=session.calendar_url,
                              colour=COLOUR)

        if session.img_url:
            embed.set_image(url=session.img_url)
        else:
            embed.set_image(url=IMG_URL)

        if session.speaker:
            embed.set_author(name=session.speaker)

        await ctx.send(f'Here\'s the next session at {str(session.start.strftime("%H:%M GMT on %B %d"))}!', embed=embed)
        await add_reactions(await ctx.channel.fetch_message(ctx.channel.last_message_id), emojis=list(ctx.guild.emojis))


@bot.after_invoke
async def after_invoke(ctx):
    await ctx.message.delete()

if __name__ == '__main__':
    main()
