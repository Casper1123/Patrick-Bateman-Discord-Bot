from discord import Interaction
from discord.ext import commands

from discorduser.logger.errors import AutocompleteErrorContext
from discorduser.user.abstract import BotClient


# todo: build whitelist or blacklist for errors into guard as param to compare Exception to list to see if it should trigger.
# Currently shit's going to spam EVERYTHING
class CustomGroupCog(commands.GroupCog):
    def __init__(self, client: BotClient):
        self.client = client

    async def autocomplete_guard(self, interaction: Interaction, current: str | int | float | bool, func, target: str):
        try:
            return await func(interaction, current)
        except Exception as e:
            await self.client.handle_exception(
                AutocompleteErrorContext(e, target, current, interaction)
            )
            return []


class CustomCog(commands.Cog):
    def __init__(self, client: BotClient):
        self.client = client

    async def autocomplete_guard(self, interaction: Interaction, current: str | int | float | bool, func, target: str):
        try:
            return await func(interaction, current)
        except Exception as e:
            await self.client.handle_exception(
                AutocompleteErrorContext(e, target, current, interaction)
            )
            return []
