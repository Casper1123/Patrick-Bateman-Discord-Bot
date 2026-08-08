from discord import app_commands, Interaction
from discord.ext import commands

from configuration.global_config import CFG
from data.interfaces.fact import FactInterface
from discorduser.user.abstract import BotClient
from piss import parse_variables, Instruction
from piss.instructionexecutor import InstructionExecutor


@app_commands.guild_only()
class FactsCog(commands.Cog):
    def __init__(self, client: BotClient, fact: FactInterface) -> None:
        self.client = client
        self.fact = fact

    @app_commands.command(name="fact", description="Gives a fact.")
    @app_commands.describe(index="The index of the fact you would like to request.")
    @app_commands.checks.cooldown(1, CFG.FACT_COOLDOWN, key=lambda i: (i.guild_id, i.user.id))
    async def fact_give(self, interaction: Interaction, index: int = None):
        try:
            fact_raw: str = self.fact.get_fact(interaction.guild_id if not self.fact.is_killswitch() else None, index)
        except IndexError:
            await self.client.user_feedback(interaction, ephemeral=True, desc=f'Index {index} is out of range.')
            return

        fact: list[Instruction] = parse_variables(fact_raw)
        executor: InstructionExecutor = InstructionExecutor(self.client)
        await executor.run(fact, interaction=interaction)

    @app_commands.command(name="fact_index", description="Gives the number of stored facts.")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
                # hardcoded 10s because this command is not as useful
                # and I'd like to save on DB calls
    async def fact_index(self, interaction: Interaction):
        global_fact_count: int = self.fact.get_fact_count(None)
        local_fact_count: int = self.fact.get_fact_count(interaction.guild_id) if not self.fact.is_killswitch() else 0
        total_fact_count: int = global_fact_count + local_fact_count
        title = "Current fact count"
        desc = f"Total: {total_fact_count}\n" \
               f"Global: {global_fact_count}\n" \
               f"Local: {local_fact_count}\n" \
               f"Index range: **{'NONE' if not total_fact_count else f'1..{total_fact_count}'}**"
        await self.client.user_feedback(interaction, ephemeral=True, title=title, desc=desc)
