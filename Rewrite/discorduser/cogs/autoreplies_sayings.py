import discord
from discord.ext import commands

import random as _r


class RandomAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener("on_message")
    async def random_saying_replies(self, message: discord.Message): # todo: rename 'saying', like what the fuck is this dude.
        if message.author.bot:
            return

        if _r.randint(1, 300) != 1:
            return

        raise NotImplementedError()
        await message.reply(mention_author=False,
                            content=process_variables(self.cm.sayings.get_line(None), self.cm.facts_manager, message,
                                                      self.client))