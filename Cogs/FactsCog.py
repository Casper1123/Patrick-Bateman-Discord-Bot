import discord
from discord import app_commands
from discord.ext import commands

from Managers.ConstantsManager import ConstantsManager
from Managers.VariableParser import process_variables


class FactsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, constants_manager: ConstantsManager) -> None:
        self.bot = bot
        self.cm = constants_manager

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    async def fact_give(self, interaction: discord.Interaction, index: int = None):
        fact: str = self.cm.facts_manager.get_fact(interaction.guild_id, index)

        await interaction.response.send_message(
            content=process_variables(fact, self.cm.facts_manager, interaction, self.bot))

    @app_commands.command(name="fact_index", description="Gives the amount of stored facts.")
    async def fact_index(self, interaction: discord.Interaction):
        global_facts, local_facts = self.cm.facts_manager.get_facts(None), self.cm.facts_manager.get_facts(interaction.guild_id)
        embed = discord.Embed(title="Current Facts",
                              description=f"Global: {len(global_facts)}\nLocal: {len(local_facts)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
