import discord
from discord import app_commands
from discord.ext import commands

from .. import BotClient
from ...data.data_interface_abstracts import DataInterface
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor


class FactsCog(commands.Cog):
    def __init__(self, client: BotClient,  db: DataInterface) -> None:
        self.client = client
        self.db = db

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    async def fact_give(self, interaction: discord.Interaction, index: int = None, ephemeral: bool = False):
        try:
            fact_raw: str = self.db.get_fact(interaction.guild_id if not self.client.local_fact_kill_switch else None, index)
        except IndexError:
            fact: str = f"Given index {index} is out of range." # todo: embed nicely
            await interaction.response.send_message(fact, ephemeral=True)
        else:
            fact: list[Instruction] = parse_variables(fact_raw)
            executor: InstructionExecutor = InstructionExecutor(self.client)
            await executor.run(fact, interaction=interaction)


    @app_commands.command(name="fact_index", description="Gives the number of stored facts.")
    async def fact_index(self, interaction: discord.Interaction):
        global_fact_count: int = self.db.get_fact_count(None)
        local_fact_count: int = self.db.get_fact_count(interaction.guild_id) if not self.client.local_fact_kill_switch else 0
        embed = discord.Embed(title="Current fact count",
                              description=f"Total: {global_fact_count + local_fact_count}\n"
                                          f"Global: {global_fact_count}\n"
                                          f"Local: {local_fact_count}")
        await interaction.response.send_message(embed=embed, ephemeral=True)