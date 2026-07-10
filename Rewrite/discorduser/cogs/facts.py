import discord
from discord import app_commands
from discord.ext import commands

from .. import BotClient
from Rewrite.data.interfaces.data import DataInterface
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor

FACT_COOLDOWN: float = 1.0


class FactsCog(commands.Cog):
    def __init__(self, client: commands.Bot, db: DataInterface) -> None:
        self.client = client
        self.db = db

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    @app_commands.checks.cooldown(1, FACT_COOLDOWN, key=lambda i: (i.guild_id, i.user.id))
    async def fact_give(self, interaction: discord.Interaction, index: int = None):
        try:
            fact_raw: str = self.db.get_fact(interaction.guild_id if not self.db.is_killswitch() else None, index)
        except IndexError:
            fact: str = f"Given index {index} is out of range." # todo: embed nicely
            await interaction.response.send_message(fact, ephemeral=True)
            return

        fact: list[Instruction] = parse_variables(fact_raw)
        executor: InstructionExecutor = InstructionExecutor(self.client, self.db)
        await executor.run(fact, interaction=interaction)


    @app_commands.command(name="fact_index", description="Gives the number of stored facts.")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
                # hardcoded 10s because this command is not as useful
                # and I'd like to save on DB calls
    async def fact_index(self, interaction: discord.Interaction):
        global_fact_count: int = self.db.get_fact_count(None)
        local_fact_count: int = self.db.get_fact_count(interaction.guild_id) if not self.db.is_killswitch() else 0
        total_fact_count: int = global_fact_count + local_fact_count
        embed = discord.Embed(title="Current fact count",
                              description=f"Total: {total_fact_count}\n"
                                          f"Global: {global_fact_count}\n"
                                          f"Local: {local_fact_count}\n"
                                          f"Index range: **{'NONE' if not total_fact_count else f'1..{total_fact_count}'}**")
        await interaction.response.send_message(embed=embed, ephemeral=True)