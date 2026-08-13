import random as _r
import re as _re

import discord
from discord import app_commands
from discord.ext import commands

from data.interfaces.autoreplies import TextAutoreplyInterface, SimpleAliasData, SimpleReplyData
from data.interfaces.pref import PreferencesInterface
from discorduser.user.abstract import BotClient
from piss import Instruction, parse_variables
from piss.instructionexecutor import InstructionExecutor

@app_commands.guild_only()
class MessageContentAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, pref: PreferencesInterface, replies: TextAutoreplyInterface) -> None:
        self.client = client
        self.pref = pref
        self.repl = replies

    @commands.Cog.listener("on_message")
    async def message_content_replies(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return
        if not self.pref.is_user_autoreply_enabled(message.author.id, 'text'):
            return
        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'text'):
            return

        a_data = self.repl.get_triggers_by_alias()

        triggering_aliases: list[SimpleAliasData] = []

        for alias, triggers in a_data.items():
            for trigger in triggers:
                # Calculate if the trigger would be accepted
                num: int = _r.randint(1, 256)
                rate: int = (trigger.rate if trigger.rate else alias.rate)
                if num > rate:
                    continue

                # For each trigger type, try to match. Raising exception if not to enforce compatibility of types.
                if trigger.type == 'regex':
                    match = _re.match(trigger.data, message.content)
                    if match:
                        triggering_aliases.append(alias)
                        break  # Prevent repeated entries of same Alias
                else:
                    raise TypeError(f'Trigger of invalid type **{trigger.type}**')
        if not triggering_aliases:
            return

        reply: SimpleReplyData | None = None
        while reply is None and triggering_aliases:
            index: int = _r.randint(0, len(triggering_aliases) - 1)
            alias: SimpleAliasData = triggering_aliases.pop(index)
            reply: SimpleReplyData | None = self.repl.get_reply(alias.name)  # Can throw an error on bad Alias name.
            # However, if that happens, we wanna pass it through.
        if not reply:
            return
            # also do not be a dumbo and put a cooldown on that log pretty please.

        if reply.type == 'text':
            instructions: list[Instruction] = parse_variables(reply.data)
            executor: InstructionExecutor = InstructionExecutor(self.client)
            await executor.run(instructions, message)
        elif reply.type == 'reaction':
            reactions: list[str] = reply.data.split(';')
            for reaction in reactions:
                await message.add_reaction(reaction)
        else:
            raise TypeError(f'Reply of invalid type **{reply.type}**')
