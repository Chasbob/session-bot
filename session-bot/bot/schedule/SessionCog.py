import datetime
import logging
from typing import List

import discord
from discord.ext import commands
from discord.ext import tasks

from . import cal
from ..utils import add_reactions
from ...util.timeTools import calc_abs_time_delta, get_time_diff


class SessionCog(commands.Cog):
    interval: int

    looper: discord.ext.tasks.Loop

    color: int

    img_url: str

    events_channel: discord.TextChannel

    roles: List[discord.Role]


    def __init__(self, bot, interval, colour, img_url, roles, events_channel):
        self.bot = bot
        self.interval = interval
        self.colour = colour
        self.img_url = img_url
        self.roles = roles
        self.events_channel = events_channel
        self.logger = logging.getLogger('session-bot')
        self.looper.change_interval(seconds=interval)
        self.looper.start()


    def cog_unload(self):
        self.looper.cancel()


    @tasks.loop()
    async def looper(self):
        session = cal.get_next_session()
        if session:
            await self.set_status(session)
            try:
                announcement_time_first = (session.start - datetime.timedelta(minutes=15))
                announcement_time_last = (session.start - datetime.timedelta(minutes=3))
                if self.check_times(announcement_time_first):
                    await self.send_long_announcement(session)
                elif self.check_times(announcement_time_last):
                    await self.send_short_announcement(session)
            except Exception as e:
                self.logger.warning(f"Session was invalid: {e}")


    async def send_long_announcement(self, session):

        embed = discord.Embed(title=session.title,
                              description=session.description,
                              url=session.url,
                              colour=self.colour)

        if session.img_url:
            embed.set_image(url=session.img_url)
        else:
            embed.set_image(url=self.img_url)
        if session.speaker:
            embed.set_author(name=session.speaker)

        await self.events_channel.send(
            f'Hey {", ".join(f"{role.mention}" for role in self.roles)} - We have a session in {get_time_diff(session.start)} minutes! :tada:\n ({str(session.start.strftime("%H:%M GMT"))})',
            embed=embed)
        await add_reactions(await self.events_channel.fetch_message(self.events_channel.last_message_id))
        self.logger.info("Long announcement made")


    async def send_short_announcement(self, session):
        await self.events_channel.send(
            f'Just {get_time_diff(session.start)} minutes until we have **{session.title}**! :tada:\n {session.url}\n{", ".join(f"{role.mention}" for role in self.roles)}')
        await add_reactions(await self.events_channel.fetch_message(self.events_channel.last_message_id))
        self.logger.info("Short announcement made")


    @commands.command(name='announce', description='manual trigger announcement')
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx: commands.Context, *, short: bool = False):
        session = cal.get_next_session()
        if session:
            if short:
                await self.send_short_announcement(session)
            else:
                await self.send_long_announcement(session)


    async def set_status(self, session):
        twitch_url = "https://twitch.tv"
        title = f"{session.title} {get_time_diff(session.start, self.interval)}"
        if session.url[:len(twitch_url)] == twitch_url:
            activity = discord.Streaming(name=title,
                                         url=session.url,
                                         platform="Twitch", )
        else:
            activity = discord.Activity(name=title,
                                        type=discord.ActivityType.watching)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)


    def check_times(self, announcement_time):
        diff = calc_abs_time_delta(announcement_time)
        return diff.total_seconds() < self.interval / 2
