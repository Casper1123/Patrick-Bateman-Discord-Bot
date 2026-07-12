import random as _r
import re as _re

import discord
from discord.ext import commands

from Rewrite.data.interfaces.autoreplies import TextAutorepliesInterface, AliasData, TriggerData, ReplyData
from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.piss import Instruction, parse_variables
from Rewrite.piss.instructionexecutor import InstructionExecutor

class MessageContentAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot, db: DataInterface, pref: PreferencesInterface, replies: TextAutorepliesInterface) -> None:
        self.client = client
        self.db = db
        self.pref = pref
        self.repl = replies

    @commands.Cog.listener("on_message")
    async def message_content_replies(self, message: discord.Message):
        if message.author.bot:
            return

        if not self.pref.is_user_autoreply_enabled(message.author.id, 'text'):
            return
        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'text'):
            return

        # Get trigger data
        # Find if a trigger is met
        # Compute if the alias should trigger
        # Randomly select from resulting aliases
        # Get a reply for that alias
        # Execute
        a_data = self.repl.get_triggers_by_alias()

        triggering_aliases: list[AliasData] = []

        for alias, triggers in a_data.items():
            for trigger in triggers:
                # Calculate if the trigger would be accepted
                if _r.randint(1, 256) < (trigger.rate if trigger.rate else alias.rate):
                    continue

                # For each trigger type, try to match. Raising exception if not to enforce compatibility of types.
                if trigger.type == 'regex':
                    match = _re.match(trigger.data, message.content)
                    if match:
                        triggering_aliases.append(alias)
                        break # continue to next alias
                else:
                    raise TypeError(f'Trigger of invalid type **{trigger.type}**')
        if not triggering_aliases:
            return

        raw: str | None = None
        while raw is None and triggering_aliases:
            index: int = _r.randint(0, len(triggering_aliases) - 1)
            alias: AliasData = triggering_aliases.pop(index)
            raw: str = self.repl.get_reply(alias.name)
        if not raw:
            return # todo: log that the given message triggered a bunch of aliases, but did not get a reply. Maybe even log which aliases it were and the trigger it hit.

        instructions: list[Instruction] = parse_variables(raw)
        executor: InstructionExecutor = InstructionExecutor(self.client, self.db)
        await executor.run(instructions, message)

