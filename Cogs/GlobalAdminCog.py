import io

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from Managers.ConstantsManager import ConstantsManager
from Managers.ReplyManager import ReplyData
from Managers.json_tools import load_json


@app_commands.default_permissions(administrator=True)
@app_commands.guilds(*[discord.Object(id=i) for i in load_json("constants.json")["global_edits_server_id"]])
class GlobalAdminGroup(commands.GroupCog, name="global"):
    def __init__(self, bot: commands.Bot, constants_manager: ConstantsManager) -> None:
        self.bot = bot
        self.cm = constants_manager
        super().__init__()

    # Facts Global
    @app_commands.command(name="fact_add", description="Adds a global fact.")
    @app_commands.describe(fact="Adds the fact")
    async def fact_global_add(self, interaction: discord.Interaction, fact: str):
        await interaction.response.defer(ephemeral=True, thinking=False)

        self.cm.facts_manager.add_global_fact(fact)
        index = self.cm.facts_manager.get_index(None, fact)

        if index is None:
            await interaction.edit_original_response(content="Sadly the new fact was not added. Weird.")
            return
        await interaction.edit_original_response(content=f"New fact added at index {index}. Enjoy!")

    @app_commands.command(name="fact_remove", description="Removes a global fact.")
    @app_commands.describe(
        index="The index of the fact you're trying to remove. Shows nearby facts' first 20 characters.")
    async def fact_global_remove(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer(ephemeral=True, thinking=False)
        if not 0 <= index - 1 < len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[0]):
            await interaction.edit_original_response(
                embed=discord.Embed(title="Index error", description="The given index is out of range."))
            return

        fact = self.cm.facts_manager.get_fact(None, index)
        self.cm.facts_manager.remove_fact(interaction.guild_id, index + index)

        embed = discord.Embed(title="Fact removed", description=f"Index: {index}\nFact:\n*{fact}*")
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="fact_edit", description="edits a global fact.")
    @app_commands.describe(
        index="The index of the fact you're trying to edit. Shows nearby facts' first 20 characters.",
        fact="The new fact to go in it's place. Technically it's an edit.")
    async def fact_global_edit(self, interaction: discord.Interaction, index: int, fact: str):
        await interaction.response.defer(ephemeral=True, thinking=False)
        if not 0 <= index - 1 < len(self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)[0]):
            await interaction.edit_original_response(
                embed=discord.Embed(title="Index error", description="The given index is out of range."))
            return

        old_fact = self.cm.facts_manager.get_fact(None, index)
        self.cm.facts_manager.edit_fact(interaction.guild_id, index, fact)

        embed = discord.Embed(title="Fact edited",
                              description=f"Index: {index}\nFrom:\n*{old_fact}*\n\nTo:\n*{fact}*")
        await interaction.edit_original_response(embed=embed)

    @fact_global_edit.autocomplete("index")
    @fact_global_remove.autocomplete("index")
    async def _autofill_callback_index(self, interaction: discord.Interaction, current: str):
        if current == "":
            current = 1

        global_facts, local_facts = self.cm.facts_manager.get_facts(interaction.guild_id, seperate=True)
        total_entries = 4  # Total choices to return
        max_messagelenght = 20

        if len(global_facts) <= total_entries:
            return [
                Choice(
                    name=f"{i + 1} : {f[:max_messagelenght]}",
                    value=i + 1
                )
                for i, f in enumerate(global_facts)
            ]

        try:
            current = int(current)
        except TypeError:
            current = 1
        except ValueError:
            current = 1

        if not 0 <= current - 1 <= len(global_facts):
            if current < 1:
                current = 1
            else:
                current = len(global_facts)

        half_window = total_entries // 2
        current -= 1  # convert to list index

        start = current - half_window
        end = current + half_window
        if start < 0:
            end += abs(start)
            start = 0
        elif end >= len(global_facts):
            temp = len(global_facts) - end
            start -= half_window - temp

        output = []
        for i, f in enumerate(global_facts[start: end]):
            output.append(Choice(
                name=f"{i + start + 1} : {f[:max_messagelenght]}",
                value=i + start + 1
            ))

        return output

    @app_commands.command(name="fact_index", description="Loads all global facts into a file.")
    async def fact_global_listall(self, interaction: discord.Interaction):
        global_facts: list[str] = self.cm.facts_manager.get_facts(None)
        file_content = "\n".join([f"{i}: {fact}" for i, fact in enumerate(global_facts)])

        embed = discord.Embed(title="Full data in attached file.")

        with io.StringIO(file_content) as text_stream:
            file = discord.File(fp=text_stream, filename=f"global_fact_data.txt")

            await interaction.response.send_message(embed=embed, ephemeral=True, file=file)

    # Replies Global
    @app_commands.command(name="alias_info", description="Gives all global-reply aliases or more detailed information.")
    @app_commands.describe(
        alias="Optional parameter that instead displays minor (or complete) information about an alias. If left empty, returns a list of aliases instead",
        complete="Whether to include a file containing the complete information of an alias.")
    async def replies_global_index(self, interaction: discord.Interaction, alias: str = None, complete: bool = False):
        if alias is None:
            await self.all_alias_list(interaction, complete)
            return
        if alias not in [e.alias for e in self.cm.reply_manager.get_aliases()]:
            await interaction.response.send_message(content="The given alias was not found.", ephemeral=True)
            return

        alias_data: ReplyData = self.cm.reply_manager.get_alias(alias)

        title: str = f"Alias data for '{alias}'"
        embed = discord.Embed(
            title=title if not complete else "Complete a" + title.removeprefix("A"),
            description="Please see attached file for complete data." if complete else
            f"Trigger count: **{len(alias_data.triggers)}**\nReply count: **{len(alias_data.replies)}**"
        )
        if not complete:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        file_content = f"# Triggers:\n"
        for trigger in alias_data.triggers:
            file_content += trigger + "\n"
        file_content += "\n# Replies:\n"
        for reply in alias_data.replies:
            file_content += f"{reply.weight}".ljust(3) + f" : {reply.value}\n"

        with io.StringIO(file_content) as text_stream:
            file = discord.File(fp=text_stream, filename=f"{alias}_data.txt")

            await interaction.response.send_message(embed=embed, ephemeral=True, file=file)

    async def all_alias_list(self, interaction: discord.Interaction, complete: bool):
        if not complete:
            try:
                await interaction.response.send_message(embed=discord.Embed(title="Alias list", description=", ".join(
                    [e.alias for e in self.cm.reply_manager.get_aliases()])), ephemeral=True)
            except ValueError:
                file_content: str = "\n".join([e.alias for e in self.cm.reply_manager.get_aliases()])
                with io.StringIO(file_content) as text_stream:
                    file = discord.File(fp=text_stream, filename=f"alias_data.txt")
                    await interaction.response.send_message(embed=discord.Embed(title="Alias list",
                                                                                description="The list of aliases was too long to display here. Check the file instead."),
                                                            file=file, ephemeral=True)
            finally:
                return

        file_content: str = ""
        for alias in self.cm.reply_manager.get_aliases():
            file_content += f"### {alias.alias}\n"
            file_content += "# Triggers\n"
            for trigger in alias.triggers:
                file_content += f"\t{trigger}\n"
            file_content += "\n# Replies\n"
            for reply in alias.replies:
                file_content += f"\t{reply.weight}".ljust(3) + f" : {reply.value}\n"
            file_content += "\n\n"
        with io.StringIO(file_content) as text_stream:
            file = discord.File(fp=text_stream, filename="alias_data.txt")
            await interaction.response.send_message(embed=discord.Embed(title="Alias Information",
                                                                        description="See the attached file for full Alias information"),
                                                    file=file, ephemeral=True)

    @app_commands.command(name="add_reply", description="Attach a new reply to an alias.")
    @app_commands.describe(alias="The alias to attach the reply to. Will create a new one if not found.",
                           reply="The reply you would like to add.",
                           weight="The % chance to be able to reply with this message. Range 1 - 100, default 100.")
    async def replies_add_reply(self, interaction: discord.Interaction, alias: str, reply: str, weight: int = None):
        if alias not in [e.alias for e in self.cm.reply_manager.get_aliases()]:
            self.cm.reply_manager.add_alias(alias)
        self.cm.reply_manager.add_reply(alias, reply, weight)

        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(title="Reply added",
                                                                                    description=f"Alias: {alias}\nReply: **{reply}**"))

    @app_commands.command(name="remove_reply", description="Removes a reply")
    @app_commands.describe(alias="The alias you'd like to remove a reply from.",
                           reply="The reply you'd like to remove.")
    async def replies_remove_reply(self, interaction: discord.Interaction, alias: str, reply: str):
        try:
            alias = [entry for entry in self.cm.reply_manager.get_aliases() if entry.alias == alias][0]
        except IndexError:
            await interaction.response.send_message(ephemeral=True, content="Given alias was not found.")
            return
        if reply not in alias.replies:
            await interaction.response.send_message(ephemeral=True, content="Given reply was not found.")
            return

        self.cm.reply_manager.remove_reply(alias.alias, alias.get_replies().index(reply) + 1)

        removed = False
        if not (alias.triggers or alias.replies):
            self.cm.reply_manager.remove_alias(alias.alias)
            removed = True

        description = "Reply removed."
        if removed:
            description += "\nAlias removed because it was empty."
        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(title=description))

    @app_commands.command(name="add_trigger", description="Attach a new trigger to an alias.")
    @app_commands.describe(alias="The alias to attach the trigger to. Will create a new one if not found.",
                           trigger="The trigger you would like to add.")
    async def replies_add_trigger(self, interaction: discord.Interaction, alias: str, trigger: str):
        if alias not in [e.alias for e in self.cm.reply_manager.get_aliases()]:
            self.cm.reply_manager.add_alias(alias)
        self.cm.reply_manager.add_trigger(alias, trigger)

        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(title="Trigger added",
                                                                                    description=f"Alias: {alias}\nTrigger: **{trigger}**"))

    @app_commands.command(name="remove_trigger", description="Removes a trigger")
    @app_commands.describe(alias="The alias you'd like to remove a trigger from.",
                           trigger="The trigger you'd like to remove.")
    async def replies_remove_trigger(self, interaction: discord.Interaction, alias: str, trigger: str):
        try:
            alias = [entry for entry in self.cm.reply_manager.get_aliases() if entry.alias == alias][0]
        except IndexError:
            await interaction.response.send_message(ephemeral=True, content="Given alias was not found.")
            return
        if trigger not in alias.triggers:
            await interaction.response.send_message(ephemeral=True, content="Given trigger was not found.")
            return

        self.cm.reply_manager.remove_trigger(alias.alias, alias.triggers.index(trigger) + 1)

        removed = False
        if not (alias.triggers or alias.replies):
            self.cm.reply_manager.remove_alias(alias.alias)
            removed = True

        description = "Trigger removed."
        if removed:
            description += "\nAlias removed because it was empty."
        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(title=description))

    # Replies autocomplete
    @replies_add_reply.autocomplete("alias")
    @replies_remove_reply.autocomplete("alias")
    @replies_add_trigger.autocomplete("alias")
    @replies_remove_trigger.autocomplete("alias")
    @replies_global_index.autocomplete("alias")
    async def _autofill_callback_global_alias(self, interaction: discord.Interaction, current: str):
        return [
            Choice(name=entry.alias, value=entry.alias) for entry in self.cm.reply_manager.get_aliases() if
            entry.alias.lower().__contains__(current.lower())
        ]

    @replies_remove_reply.autocomplete("reply")
    async def _autofill_callback_reply(self, interaction: discord.Interaction, current: str):
        try:
            alias = \
            [entry for entry in self.cm.reply_manager.get_aliases() if entry.alias == interaction.namespace.alias][0]
        except IndexError:
            return []
        return [
                   Choice(name=f"{str(reply.weight).ljust(3)}: {reply.value[:10]}", value=reply.value) for reply in
                   alias.replies if reply.value.lower().__contains__(current)
               ][:3]

    @replies_remove_trigger.autocomplete("trigger")
    async def _autofill_callback_trigger(self, interaction: discord.Interaction, current: str):
        # todo: show weights.
        try:
            alias = \
            [entry for entry in self.cm.reply_manager.get_aliases() if entry.alias == interaction.namespace.alias][0]
        except IndexError:
            return []
        return [
                   Choice(name=trigger[:10], value=trigger) for trigger in alias.triggers if
                   trigger.lower().__contains__(current)
               ][:3]

    # Global Bouncerlines
    @app_commands.command(name="line_add", description="Adds a randomly used line.")
    @app_commands.describe(line="The line to add.")
    async def line_global_add(self, interaction: discord.Interaction, line: str):
        await interaction.response.defer(ephemeral=True, thinking=False)

        self.cm.sayings.add_line(line)
        index = self.cm.sayings.get_index(line)

        if index is None:
            await interaction.edit_original_response(content="Sadly the new line was not added. Weird.")
            return
        await interaction.edit_original_response(content=f"New line added at index {index}. Enjoy!")

    @app_commands.command(name="line_remove", description="Removes a randomly used line.")
    @app_commands.describe(
        index="The index of the line you're trying to remove. Shows nearby line's first 20 characters.")
    async def line_global_remove(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer(ephemeral=True, thinking=False)
        if not 0 <= index - 1 < len(self.cm.sayings.get_lines()):
            await interaction.edit_original_response(
                embed=discord.Embed(title="Index error", description="The given index is out of range."))
            return

        fact = self.cm.sayings.get_line(index)
        self.cm.sayings.remove_line(index)

        embed = discord.Embed(title="Line removed", description=f"Index: {index}\nFact:\n*{fact}*")
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="line_edit", description="edits a randomly used line.")
    @app_commands.describe(
        index="The index of the line you're trying to edit. Shows nearby line's first 20 characters.",
        line="The new line to go in it's place. Technically it's an edit.")
    async def line_global_edit(self, interaction: discord.Interaction, index: int, line: str):
        await interaction.response.defer(ephemeral=True, thinking=False)
        if not 0 <= index - 1 < len(self.cm.sayings.get_lines()):
            await interaction.edit_original_response(
                embed=discord.Embed(title="Index error", description="The given index is out of range."))
            return

        old_line = self.cm.sayings.get_line(index)
        self.cm.sayings.edit_line(index, line)

        embed = discord.Embed(title="Line edited",
                              description=f"Index: {index}\nFrom:\n*{old_line}*\n\nTo:\n*{line}*")
        await interaction.edit_original_response(embed=embed)

    @fact_global_edit.autocomplete("index")
    @fact_global_remove.autocomplete("index")
    async def _autofill_callback_line_index(self, interaction: discord.Interaction, current: str):
        if current == "":
            current = 1

        lines = self.cm.sayings.get_lines()
        total_entries = 4  # Total choices to return
        max_messagelenght = 20
        try:
            current = int(current)
        except TypeError as err:
            current = 1
        except ValueError as err:
            current = 1

        if len(lines) <= total_entries:
            return [
                Choice(
                    name=f"{i + 1} : {f[:max_messagelenght]}",
                    value=i + 1
                )
                for i, f in enumerate(lines)
            ]

        if not 0 <= current - 1 <= len(lines):
            if current < 1:
                current = 1
            else:
                current = len(lines)

        half_window = total_entries // 2
        current -= 1  # convert to list index

        start = current - half_window
        end = current + half_window
        if start < 0:
            end += abs(start)
            start = 0
        elif end >= len(lines):
            temp = len(lines) - end
            start -= half_window - temp

        output = []
        for i, f in enumerate(lines[start: end]):
            output.append(Choice(
                name=f"{i + start + 1} : {f[:max_messagelenght]}",
                value=i + start + 1
            ))

        return output

    @app_commands.command(name="line_index", description="Loads all randomly used lines into a file.")
    async def line_listall(self, interaction: discord.Interaction):
        lines: list[str] = self.cm.sayings.get_lines()
        file_content = "\n".join([f"{i + 1}: {fact}" for i, fact in enumerate(lines)])

        embed = discord.Embed(title="Full data in attached file.")

        with io.StringIO(file_content) as text_stream:
            file = discord.File(fp=text_stream, filename=f"lines_data.txt")

            await interaction.response.send_message(embed=embed, ephemeral=True, file=file)
