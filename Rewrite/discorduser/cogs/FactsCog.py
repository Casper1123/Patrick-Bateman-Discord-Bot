import discord
from discord import app_commands
from discord.ext import commands

from ...variables_parser import parse_variables

class FactsCog(commands.Cog):
    # todo: db reachable class needs type definition
    def __init__(self, client: commands.bot,  db, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    async def fact_give(self, interaction: discord.Interaction, index: int = None, ephemeral: bool = False):
        try:
            fact_raw: str = self.db.getFact(interaction.guild_id, index)  # todo: handle index out of range error thrown by db
        except IndexError:
            fact: str = f"Given index {index} is out of range."
        else:
            fact: str = parse_variables(fact_raw)

        await interaction.response.send_message(fact, ephemeral=ephemeral)

    @app_commands.command(name="fact_index", description="Gives the number of stored facts.")
    async def fact_index(self, interaction: discord.Interaction):
        # obtain number of global facts
        global_fact_count: int = self.db.getFactCount(None)
        # obtain number of local facts
        local_fact_count: int = self.db.getFactCount(interaction.guild_id)
        # send data over.