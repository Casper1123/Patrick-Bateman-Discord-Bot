import discord
from discord import app_commands
from discord.ext import commands

from .. import BotClient
from ...data.data_interface_abstracts import DataInterface
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor

FACT_COOLDOWN: float = 1.0


class FactsCog(commands.Cog):
    def __init__(self, client: BotClient,  db: DataInterface) -> None:
        self.client = client
        self.db = db

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    @app_commands.checks.cooldown(1, FACT_COOLDOWN, key=lambda i: (i.guild_id, i.user.id))
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
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
                # hardcoded 10s because this command is not as useful
                # and I'd like to save on DB cals
    async def fact_index(self, interaction: discord.Interaction):
        global_fact_count: int = self.db.get_fact_count(None)
        local_fact_count: int = self.db.get_fact_count(interaction.guild_id) if not self.client.local_fact_kill_switch else 0
        embed = discord.Embed(title="Current fact count",
                              description=f"Total: {global_fact_count + local_fact_count}\n"
                                          f"Global: {global_fact_count}\n"
                                          f"Local: {local_fact_count}")
        await interaction.response.send_message(embed=embed, ephemeral=True)