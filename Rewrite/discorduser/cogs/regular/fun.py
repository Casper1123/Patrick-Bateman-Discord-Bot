import datetime
import random as _r

import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.utilities.messagevisualisation import embedify

@app_commands.guild_only()
class MainCommandsCog(commands.Cog):
    def __init__(self, client: BotClient) -> None:
        self.client = client

    @app_commands.command(name="chinesenukelaunchcodes",
                          description="速度与激情早上好中国现在我有冰激淋 我很喜欢冰激淋但是《速度与激情9》比冰激淋……🍦")
    async def chinese_nuke_launch_codes(self, interaction: discord.Interaction):
        numlist = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "零"] # todo: update the text
        numbers = "".join([_r.choice(numlist) for _ in range(_r.randint(8, 12))])
        await interaction.response.send_message(
            content=f"哦，亲爱的中华人民共和国领导人，愿您带领我们走向胜利。 准备好你的发射代码，用一阵核辐射来征服胖子的土地。 赞美习近平，赞美中共，赞美中国！ ： {numbers}",
            ephemeral=False)

    @app_commands.command(name="throwitback", description="...")
    async def throw_it_back(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="https://tenor.com/view/throw-it-back-gif-25029115")

    @app_commands.command(name="sex", description="sex")
    async def _sex(self, interaction: discord.Interaction):
        await interaction.response.send_message("Yeah, no.")
        # todo: update

    @app_commands.command(name="throwback", description="Replies to a random message in this channel's history.")
    @app_commands.describe(ephemeral="Hide the response; sneaky private throwback")
    async def throwback_command(self, interaction: discord.Interaction, ephemeral: bool = False):
        await interaction.response.send_message("Finding random message in channel history. This might take some time.",
                                                ephemeral=ephemeral)
        # Get current last message date
        newest: datetime.datetime = \
        [message async for message in interaction.channel.history(limit=1, oldest_first=False)][0].created_at
        # Get current oldest message date
        oldest: datetime.datetime = \
        [message async for message in interaction.channel.history(limit=1, oldest_first=True)][0].created_at

        if not oldest or not newest:
            await interaction.edit_original_response(content='Insufficient messages found')
            return

        random_message: discord.Message | None = None
        total_seconds = int((newest - oldest).total_seconds())
        attempts: int = 0
        while random_message is None and attempts < 100:
            # Create a new date in between based on random seconds in between.
            random_seconds = _r.randint(0, total_seconds)
            random_date = oldest + datetime.timedelta(seconds=random_seconds)

            messages: list[discord.Message] = [message async for message in
                                               interaction.channel.history(limit=1, around=random_date)]
            if messages:
                random_message = messages[0]
            else:
                attempts += 1

        if attempts >= 100:
            await interaction.edit_original_response(content="Could not find a message within a reasonable timeframe.")
            return

        embeds: list[discord.Embed] = await embedify(self.client, random_message, reply=True, message_jump_link=True)
        await interaction.edit_original_response(embeds=embeds)
