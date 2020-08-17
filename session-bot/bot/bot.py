import os
import sys
import asyncio
import pytz
import datetime
import random
import discord
import logging

from discord.ext import commands
from discord.http import LoginFailure
from .schedule import cal

from ..util import config
from ..util.log import fatal_error


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
        events_channel_id = int(config.config['discord']['events_id'])
        guild_id = int(config.config['discord']['guild_id'])
        role_ids = list(map(lambda x: int(x), config.config['discord']['roles']))
        if not token:
            fatal_error(f"msg=\"Token was missing!\"")
    except Exception as e:
        fatal_error(f"msg=\"error parsing environment variables\", error=\"{e}\"")

    bot.loop.create_task(check_schedule())
    bot.run(token)

async def check_schedule():
    await bot.wait_until_ready()

    global events_channel, events_channel_id, guild_id, role_ids, roles
    events_channel = bot.get_channel(events_channel_id)
    roles = []
    for role_id in role_ids:
        roles.append(bot.get_guild(guild_id).get_role(role_id))

    while True:
        session = cal.get_next_session()
        if session != None:
            await set_status(session)
            try:
                announcement_time_first = (session.start - datetime.timedelta(minutes=15))
                announcement_time_last = (session.start - datetime.timedelta(minutes=3))
                if check_times(announcement_time_first):
                    await send_long_announcement(session)
                elif check_times(announcement_time_last):
                    await send_short_announcement(session)
            except Exception as e:
                logger.warning(f"Session was invalid: {e}")
        await asyncio.sleep(interval)

async def set_status(session):
    twitch_url = "https://twitch.tv"
    title = f"{session.title} {get_time_diff(session.start)}"
    if session.url[:len(twitch_url)] == twitch_url:
        activity = discord.Streaming(name=title,
                                        url=session.url,
                                        platform="Twitch",)
    else:
        activity = discord.Activity(name=title,
                                    type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.online, activity=activity)

async def send_long_announcement(session):
    global events_channel, roles

    embed = discord.Embed(title=session.title,
                        description=session.description,
                        url=session.url,
                        colour=COLOUR)

    embed.set_footer(text=session.url)

    if session.img_url != None:
        embed.set_image(url=session.img_url)
    else:
        embed.set_image(url=IMG_URL)
    if session.speaker != None:
        embed.set_author(name=session.speaker)

    await events_channel.send(f'Hey {", ".join(f"{role.mention}" for role in roles)} - We have a session in 15 minutes! :tada:\n ({str(session.start.strftime("%H:%M GMT"))})', embed=embed)
    await add_reactions(await events_channel.fetch_message(events_channel.last_message_id))
    logger.info("Long announcement made")

async def send_short_announcement(session):
    global events_channel, fellow_role
    await events_channel.send(f'Just 3 minutes until we have **{session.title}**! :tada:\n {session.url}\n{fellow_role.mention}')
    await add_reactions(await events_channel.fetch_message(events_channel.last_message_id))
    logger.info("Short announcement made")

def check_times(announcement_time):
    diff = calc_abs_time_delta(announcement_time)
    return diff.total_seconds() < interval / 2

def calc_abs_time_delta(announcement_time):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    announcement_time = pytz.UTC.normalize(announcement_time)
    abs_delta = abs(announcement_time - current_time)
    logger.debug(f"delta={str(abs_delta)}")
    return abs_delta


def get_time_diff(announcement_time):
    diff = calc_abs_time_delta(announcement_time)
    diff_args = str(diff).split(':')
    if (diff.total_seconds() < (interval / 2)):
        return "happening NOW!"
    else:
        return "in " + diff_args[0] + ":" + diff_args[1] + " hr"

async def add_reactions(message):
    emojis = ["💻", "🙌", "🔥", "💯", "🍕", "🎉", "🥳", "💡", "📣"]
    random.shuffle(emojis)
    for emoji in emojis[:4]:
        await message.add_reaction(emoji)


@bot.command(description="Displays next event")
async def next_session(ctx):
    session = cal.get_next_session()
    logger.info("Sending next session via command")
    if session != None:
        embed = discord.Embed(title=session.title,
                            description=f'Starting at {str(session.start.strftime("%H:%M GMT on %B %d"))}',
                            url=session.calendar_url,
                            colour=COLOUR)

        if session.img_url != None:
            embed.set_image(url=session.img_url)
        else:
            embed.set_image(url=IMG_URL)

        if session.speaker != None:
            embed.set_author(name=session.speaker)

        await ctx.send(f'Here\'s the next session at {str(session.start.strftime("%H:%M GMT on %B %d"))}!', embed=embed)
        await add_reactions(await ctx.channel.fetch_message(ctx.channel.last_message_id))

@bot.after_invoke
async def after_invoke(ctx):
    await ctx.message.delete()

if __name__ == '__main__':
    main()
