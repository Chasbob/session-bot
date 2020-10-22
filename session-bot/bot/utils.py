import random
from typing import List

import discord


async def add_reactions(message, emojis: List[discord.Emoji] = None):
    if emojis is None or len(emojis) < 4:
        emojis = ["💻", "🙌", "🔥", "💯", "🍕", "🎉", "🥳", "💡", "📣"]
    else:
        emojis = emojis.copy()
    random.shuffle(emojis)
    for emoji in emojis[:4]:
        await message.add_reaction(emoji)
