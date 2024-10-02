import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import io

from Managers.ConstantsManager import ConstantsManager
from Managers.VariableParser import process_fact


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class LocalAdminGroup(commands.GroupCog, name="admin"):
    def __init__(self, bot: commands.Bot, constants_manager: ConstantsManager) -> None:
        self.bot = bot
        self.cm = constants_manager
        super().__init__()

    # Facts Administrator
    @app_commands.command(name="add", description="Adds a server-specific fact to this server.")
    @app_commands.describe(fact="Adds the fact")
    async def fact_local_add(self, interaction: discord.Interaction, fact: str):
        if len(fact) > 200 and interaction.guild_id not in self.cm.super_server_ids:
            await interaction.response.send_message(embed=discord.Embed(title="Fact not added",
                                                                        description="The lenght of your given fact is longer than 200 characters."),
                                                    ephemeral=True)
            return

        fact_count = len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[1])
        if fact_count >= 50 and interaction.guild_id not in self.cm.super_server_ids:
            await interaction.response.send_message(
                embed=discord.Embed(title="Fact not added", description="You have reached your limit of 50 facts."),
                ephemeral=True)
            return

        # Back out if the fact is empty. Cannot send empty messages.
        if fact == "":
            await interaction.response.send_message(
                embed=discord.Embed(title="Fact not added", description="Sadly the new fact was not added. Weird."),
                ephemeral=True)
            return

        # Add entry to database and get index for reply.
        self.cm.facts_manager.add_fact(fact, interaction.guild_id)
        index = self.cm.facts_manager.get_index(interaction.guild_id, fact)

        if index is None:
            await interaction.response.send_message(
                embed=discord.Embed(title="Fact not added", description="Sadly the new fact was not added. Weird."),
                ephemeral=True)
            return
        await interaction.response.send_message(
            embed=discord.Embed(title="Fact added", description=f"New fact added at index {index}. Enjoy!"),
            ephemeral=True)

    @app_commands.command(name="remove", description="Removes a fact from this server's facts.")
    @app_commands.describe(
        index="The index of the fact you're trying to remove. Shows nearby facts' first 20 characters.")
    async def fact_local_remove(self, interaction: discord.Interaction, index: int):
        if not 0 <= index - 1 < len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[1]):
            await interaction.response.send_message(
                embed=discord.Embed(title="Index error", description="The given index is out of range."),
                ephemeral=True)
            return

        global_index = len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[0])
        fact = self.cm.facts_manager.get_fact(interaction.guild_id, global_index + index)
        self.cm.facts_manager.remove_fact(interaction.guild_id, global_index + index)

        embed = discord.Embed(title="Fact removed", description=f"Index: {index}\nFact:\n*{fact}*")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="edit", description="edits one of this server's facts.")
    @app_commands.describe(
        index="The index of the fact you're trying to edit. Shows nearby facts' first 20 characters.",
        fact="The new fact to go in it's place. Technically it's an edit.")
    async def fact_local_edit(self, interaction: discord.Interaction, index: int, fact: str):
        if len(fact) > 200 and interaction.guild_id not in self.cm.super_server_ids:
            await interaction.response.send_message(embed=discord.Embed(title="Fact not added",
                                                                        description="The lenght of your given fact is longer than 200 characters."),
                                                    ephemeral=True)
            return
        if not 0 <= index - 1 < len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[1]):
            await interaction.response.send_message(
                embed=discord.Embed(title="Index error", description="The given index is out of range."),
                ephemeral=True)
            return

        global_index = len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[0])
        old_fact = self.cm.facts_manager.get_fact(interaction.guild_id, global_index + index)
        self.cm.facts_manager.edit_fact(interaction.guild_id, global_index + index, fact)

        embed = discord.Embed(title="Fact edited", description=f"Index: {index}\nFrom:\n*{old_fact}*\n\nTo:\n*{fact}*")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="index", description="Gives a list of all local facts in file form.")
    async def fact_local_listall(self, interaction: discord.Interaction):
        local_facts: list[str] = self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[1]
        file_content = "\n".join([f"{i}: {fact}" for i, fact in enumerate(local_facts)])

        embed = discord.Embed(title="Full data in attached file.")

        with io.StringIO(file_content) as text_stream:
            file = discord.File(fp=text_stream, filename=f"local_fact_data_{interaction.guild_id}.txt")

            await interaction.response.send_message(embed=embed, ephemeral=True, file=file)

    @fact_local_edit.autocomplete("index")
    @fact_local_remove.autocomplete("index")
    async def _autofill_callback_index(self, interaction: discord.Interaction, current: int) -> list[Choice]:
        if current == "":
            current = 1

        global_facts, local_facts = self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)
        total_entries = 4  # Total choices to return
        max_messagelenght = 20

        if len(local_facts) <= total_entries:
            return [
                Choice(
                    name=f"{i + 1} : {f[:max_messagelenght]}",
                    value=i + 1
                )
                for i, f in enumerate(local_facts)
            ]

        try:
            current = int(current)
        except TypeError:
            current = 1
        except ValueError:
            current = 1

        if not 0 <= current - 1 <= len(global_facts) + len(local_facts):
            if current < 1:
                current = 1
            else:
                current = len(local_facts)

        half_window = total_entries // 2
        current -= 1  # convert to list index

        start = current - half_window
        end = current + half_window
        if start < 0:
            end += abs(start)
            start = 0
        elif end >= len(local_facts):
            temp = len(local_facts) - end
            start -= half_window - temp

        output = []
        for i, f in enumerate(local_facts[start:end]):
            output.append(Choice(
                name=f"{i + start + 1} : {f[:max_messagelenght]}",
                value=i + start + 1
            ))

        return output

    @app_commands.command(name="preview", description="Gives back the given text as a processed fact.")
    @app_commands.describe(fact="The given fact to be processed.")
    async def fact_preview(self, interaction: discord.Interaction, fact: str):
        if len(fact) > 200 and interaction.guild_id not in self.cm.super_server_ids:
            await interaction.response.send_message(embed=discord.Embed(title="Fact error",
                                                                        description="The lenght of your given fact is longer than 200 characters."),
                                                    ephemeral=True)
            return

        await interaction.response.send_message(
            embed=discord.Embed(description=process_fact(fact, self.cm.facts_manager, interaction, self.bot)), ephemeral=True)

    @app_commands.command(name="help", description="Gives information on in-fact variables.")
    async def fact_help(self, interaction: discord.Interaction):
        description = \
            "Refer to [the documentation](https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki/The-Variable-system) for detailed information.\n" \
            "**Regular Variables**\n" \
            "User:\n" \
            "\tuser.account\n\tuser.name\n\tuser.id\n\n" \
            "Channel:\n" \
            "\tchannel.name\n\tchannel.id\n\n" \
            "Guild:\n" \
            "\tguild.name\t\nguild.name\n" \
            "\tguild.owner:\n" \
            "\t\tguild.owner.account\n\t\tguild.owner.name\n\t\tguild.owner.id\n\n" \
            "Randomuser\n" \
            "\trandomuser.account\n\trandomuser.name\n\trandomuser.id\n\n" \
            "Self:\n" \
            "\tself.name\n\tself.nick\n\tself.id\n\n" \
            "General:\n" \
            "\t{enter} / '\\n'\n"\
            "\ttotal_facts\n" \
            "\tglobal_facts\n" \
            "\tlocal_facts\n\n" \
            "**Command Variables**\n" \
            "rand:\n" \
            "The number generated is between the lower and upper, inclusive.\n" \
            "\t\"{rand:lower,upper}\"\n" \
            "\t\"{rand:0,1}\"\n\n" \
            "choice: picks a random option of the strings given.\n" \
            "What's important to know is that these choices can have variables.\n" \
            "\t\"{choice:\"option\",...}\"\n" \
            "\t\"{choice:\"option 1\",\"option with {variable}\"}"


        embed = discord.Embed(
            title="Fact variables information",
            description=description
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
