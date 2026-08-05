# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, _reply_types, \
    SimpleAliasData, SimpleTriggerData, SimpleReplyData
from Rewrite.discorduser.logger import GlobalLogger
from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.piss.testing import test_raw_input as input_test
from Rewrite.utilities.autocomplete_cramming import cram_options

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input
WEIGHT_UPPER_BOUND: int = 1024

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _AliasGlobalAdminCog(commands.Cog, name='alias'):
    def __init__(self, client: BotClient, repl: GlobalTextAutorepliesInterface, logger: GlobalLogger) -> None:
        self.client = client
        self.repl = repl
        self.logger = logger

    @app_commands.command(name='create', description='Create a new Alias')
    @app_commands.describe(name='The name of the new alias. Cannot be duplicate.',
                           rate='The standard activation rate of this alias, ranging in between 1-256. Default: 256 (100%)',
                           ephemeral='Hide this command for other users.')
    async def create_alias(self, interaction: discord.Interaction, name: str, rate: int = None, ephemeral: bool = False) -> None:
        try:
            self.repl.create_alias(name, rate if rate is not None else 256)
        except ValueError:
            await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Alias creation failed',
                                                                        desc='This alias already exists.')
            return
        await self.logger.create_alias(interaction, name, rate)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Alias created successfully')

    @app_commands.command(name='edit', description='Edit an existing Alias')
    @app_commands.describe(alias='The Alias you wish to edit.',
                          new_name='The new name of the Alias.',
                          rate='The standard activation rate of this alias, ranging in between 1-256. Leave empty for 256',
                           ephemeral='Hide this command for other users.')
    @app_commands.rename(new_name='name')
    async def edit_alias(self, interaction: discord.Interaction, alias: str, new_name: str | None = None, rate: int | None = None, ephemeral: bool = False):
        if rate is None and new_name is None:
            await self.client.user_feedback(interaction, title='Alias edit failed',
                            desc='Please select an option. If you intend to delete this alias, select the pre-given option to do so.', ephemeral=ephemeral)
        if rate is not None and not (1 <= rate <= 256):
            # Rate not in domain and passed in.
            await self.client.user_feedback(interaction, title='Alias edit failed',
                desc=f'The given rate **{rate}** is not within the domain **[1..256]**.', ephemeral=ephemeral)
            return
        try:
            self.repl.edit_alias(alias, new_name if (new_name and new_name != alias) else None, rate)
        except ValueError:
            await self.client.user_feedback(interaction, title='Alias edit failed',
                                    desc='The given alias does not exist, or the new alias name is already taken.', ephemeral=ephemeral)
            return
        await self.logger.edit_alias(interaction, alias, new_name if (new_name and new_name != alias) else None, rate)
        await self.client.user_feedback(interaction, title='Alias edited successfully', ephemeral=ephemeral)

    @app_commands.command(name='delete', description='Delete an existing Alias, as well as all of its contents.')
    @app_commands.describe(alias='The Alias you wish to delete.', confirm='YOU REMOVE ALL TRIGGERS AND REPLIES TOO.', ephemeral='Hide this command for other users.')
    async def delete_alias(self, interaction: discord.Interaction, alias: str, confirm: bool = None, ephemeral: bool = False) -> None:
        if not confirm:
            await self.client.user_feedback(interaction, title='Alias removal failed', desc='Confirm your decision.\n'
                                                                                            'This is done so you have to think twice about removing the Alias.\n'
                                                                                            '**NOTE:** REMOVING THE ALIAS WILL ALSO DELETE ALL TRIGGERS AND REPLIES ATTACHED.')
            return

        try:
            self.repl.delete_alias(alias)
        except ValueError:
            await self.client.user_feedback(interaction, title='Alias removal failed', desc='Cannot delete a nonexistent Alias.', ephemeral=ephemeral)
            return
        await self.logger.delete_alias(interaction, alias)
        await self.client.user_feedback(interaction, title='Alias deleted successfully', ephemeral=ephemeral)

    # region autocomplete
    @edit_alias.autocomplete('alias')
    @delete_alias.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str):
        target = current.lower() # Prevent repeat transformation
        aliases: list[SimpleAliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]
    # endregion

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _TriggerGlobalAdminCog(commands.Cog, name='trigger'):
    def __init__(self, client: BotClient, repl: GlobalTextAutorepliesInterface, logger: GlobalLogger) -> None:
        self.client = client
        self.repl = repl
        self.logger = logger

    @app_commands.command(name='create', description='Create a new Trigger')
    @app_commands.describe(alias='The Alias this Trigger belongs to.', text='Trigger RegEx to match to.',
                           rate='The relative rate this Trigger will proc to, overriding the Alias rate if given. Range 1-256',
                           ephemeral='Hide this command for other users.')
    async def create_trigger(self, interaction: discord.Interaction, alias: str, text: str, rate: int = None, ephemeral: bool = False):
        if rate is not None and not (1 <= rate <= 256):
            await self.client.user_feedback(interaction, title='Trigger creation failed',
                      desc='The given rate is not in range **[1..256]**.', ephemeral=ephemeral)
            return
        try:
            self.repl.add_trigger(alias, trigger_type='regex', data=text, rate=rate) # todo: create and support other trigger types.
        except ValueError:
            await self.client.user_feedback(interaction, title='Trigger creation failed', desc=f'The given Alias {alias} does not exist.', ephemeral=ephemeral)
            return
        await self.logger.create_trigger(interaction, alias, 'regex', text, rate)
        await self.client.user_feedback(interaction, title='Trigger created successfully', desc=f'Alias: {alias}\n*Type: Regex*\nContent: **{text}**', ephemeral=ephemeral)

    @app_commands.command(name='edit', description='Edit a Trigger')
    @app_commands.describe(alias='The Alias this Trigger belongs to.',
                           index='The index of this trigger.',
                           text='Trigger RegEx to match to.',
                           rate='The relative rate this Trigger will proc to, overriding the Alias rate if given. Range 1-256',
                           ephemeral='Hide this command for other users.')
    # todo: index autocomplete based on passed-in alias.
    async def edit_trigger(self, interaction: discord.Interaction, alias: str, index: int, text: str = None, rate : int = None, ephemeral: bool = False):
        if text is None and rate is None:
            await self.client.user_feedback(interaction, title='Trigger edit failed',
                                            desc='You need to update at least one of text and rate.', ephemeral=ephemeral)
            return
        if rate is not None and not (1 <= rate <= 256):
            await self.client.user_feedback(interaction, title='Trigger edit failed', desc='The given rate is not in range **[1..256]**.', ephemeral=ephemeral)
            return

        try:
            old: SimpleTriggerData = self.repl.get_trigger_by_index(alias, index)
            self.repl.edit_trigger(alias, index, trigger_type='regex', data=text, rate=rate)
        except ValueError:
            await self.client.user_feedback(interaction, title='Trigger edit failed',
                                            desc='The given alias does not exist.', ephemeral=ephemeral)
            return
        except IndexError:
            await self.client.user_feedback(interaction, title='Trigger edit failed', desc='Trigger index out of bounds',
                                            ephemeral=ephemeral)
            return
        await self.logger.edit_trigger(interaction, alias, old, text, rate)
        await self.client.user_feedback(interaction, title='Trigger edited successfully', ephemeral=ephemeral)

    @app_commands.command(name='delete', description='Delete a Trigger')
    @app_commands.describe(alias='The Alias this Trigger belongs to.',
                           index='The index of this Trigger.',
                           ephemeral='Hide this command for other users.')
    # todo: index autocomplete based on passed-in alias.
    async def delete_trigger(self, interaction: discord.Interaction, alias: str, index: int, ephemeral: bool = False):
        try:
            old: SimpleTriggerData = self.repl.remove_trigger(alias, index)
        except ValueError:
            await self.client.user_feedback(interaction, title='Trigger deletion failed',
                                            desc='The given alias does not exist.', ephemeral=ephemeral)
            return
        except IndexError:
            await self.client.user_feedback(interaction, title='Trigger deletion failed',
                                            desc='Trigger index out of bounds',
                                            ephemeral=ephemeral)
            return
        await self.logger.delete_trigger(interaction, alias, old)
        await self.client.user_feedback(interaction, title='Trigger deleted successfully', ephemeral=ephemeral)

    # region autocomplete
    @create_trigger.autocomplete('alias')
    @edit_trigger.autocomplete('alias')
    @delete_trigger.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str) -> list[Choice[str]]:
        target = current.lower()  # Prevent repeat transformation
        aliases: list[SimpleAliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]

    @edit_trigger.autocomplete('index')
    @delete_trigger.autocomplete('index')
    async def _index_options_autocomplete(self, interaction: discord.Interaction, current: int) -> list[Choice[int]]:
        alias = interaction.namespace.alias
        if not alias:
            return []
        # Try and find the current alias.
        if not self.repl.alias_exists(alias):
            return [Choice(name='Bad alias.', value=-1)]
        triggers: list[SimpleTriggerData] = self.repl.get_triggers_for_alias(alias)
        # Time to compress this stuff.
        lower, upper = cram_options(len(triggers), current, 4, favour='higher')
        return [
            # Offset like this because indexing is by 1 for users.
            Choice(name=f'{offset + 1} ({trigger.type}): {trigger.data[:80]}', value=offset + 1)
            for offset, trigger in enumerate(triggers[lower:upper])
        ]
    # endregion

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _ReplyGlobalAdminCog(commands.Cog, name='reply'):
    def __init__(self, client: BotClient, repl: GlobalTextAutorepliesInterface, logger: GlobalLogger) -> None:
        self.client = client
        self.repl = repl
        self.logger = logger

    @app_commands.command(name='create', description='Create a new Reply')
    @app_commands.describe(alias='The Alias this reply will belong to.',
                            reply_type='The type of Reply this has to be.',
                           text='Raw text data for the reply. For text replies, PISS-compatible. For reaction replies, unicode emojis only.',
                           weight='The relative weight this Reply will proc to. Defaults to 1.',
                           ephemeral='Hide this command for other users.')
    @app_commands.rename(reply_type='type')
    async def create_reply(self, interaction: discord.Interaction, alias: str, reply_type: _reply_types, text: str, weight: int = 1, ephemeral: bool = False):
        if weight is not None and not 1 <= weight <= WEIGHT_UPPER_BOUND:
            await self.client.user_feedback(interaction, title='Reply creation failed', desc=f'Weight not in range [1..{WEIGHT_UPPER_BOUND}].', ephemeral=ephemeral)
        if reply_type == 'text':
            # test the reply before adding.
            if not await input_test(self.client, interaction, text, ephemeral=ephemeral):
                return
        elif reply_type == 'reaction':
            # todo: check, if reply type is reaction, that it is a string of only standard unicode emojis. Added by separating them using ;?
            await self.client.user_feedback(interaction, title='Unsupported',
                                            desc='The given Reply type is not supported.\nIt will be in the future, but right now it is not. The setting is a placeholder.',
                                            ephemeral=ephemeral)
            return
        else:
            await self.client.user_feedback(interaction, title='Reply creation failed', desc=f'Reply type {reply_type} not supported.', ephemeral=ephemeral)
        try:
            self.repl.add_reply(alias, reply_type, data=text, weight=weight)
        except ValueError:
            await self.client.user_feedback(interaction, title='Reply creation failed', desc=f'Alias {alias} does not exist.', ephemeral=ephemeral)
            return
        await self.logger.create_reply(interaction, alias, reply_type, text, weight)
        await self.client.user_feedback(interaction, title='Reply created successfully', ephemeral=ephemeral)

    @app_commands.command(name='edit', description='Edit a Reply; text and weight only!')
    @app_commands.describe(alias='The alias the reply belongs to.', index='The index of the Reply (autocomplete requires the Alias first!)',
                           ephemeral='Hide this command for other users.')
    # todo: index autocomplete based on passed-in alias.
    async def edit_reply(self, interaction: discord.Interaction, alias: str, index: int, text: str = None, weight: int = None, ephemeral: bool = False):
        if text is None and weight is None:
            await self.client.user_feedback(interaction, title='Reply edit failed', desc='You need to update at least one of text and weight.')
            return

        if weight is not None and not 1 <= weight <= WEIGHT_UPPER_BOUND:
            await self.client.user_feedback(interaction, title='Reply creation failed',
                                            desc=f'Weight not in range [1..{WEIGHT_UPPER_BOUND}].', ephemeral=ephemeral)


        try:
            old: SimpleReplyData = self.repl.get_reply_by_index(alias, index)
            # Test new input data
            if old.type == 'text':
                if not await input_test(self.client, interaction, text, ephemeral):
                    return
            elif old.type == 'reaction':
                await self.client.user_feedback(interaction, title='Reply edit failed', desc='Editing this type of reply is currently unsupported.', ephemeral=ephemeral)
                return # todo: gotta support this man.
            else:
                raise ValueError('Received reply with un accounted for type.')

            self.repl.edit_reply(alias, index, text, weight)

        except ValueError:
            await self.client.user_feedback(interaction, title='Reply edit failed', desc='The given alias does not exist.', ephemeral=ephemeral)
            return
        except IndexError:
            await self.client.user_feedback(interaction, title='Reply edit failed', desc='Reply index out of bounds', ephemeral=ephemeral)
            return

        await self.logger.edit_reply(interaction, alias, old, text, weight)
        await self.client.user_feedback(interaction, title='Reply edited successfully', ephemeral=ephemeral)

    @app_commands.command(name='delete', description='Delete a Reply.')
    @app_commands.describe(alias='The alias the reply belongs to.', index='The index of the Reply (autocomplete requires the Alias first!)',
                           ephemeral='Hide this command for other users.')
    # todo: index autocomplete based on passed-in alias.
    async def delete_reply(self, interaction: discord.Interaction, alias: str, index: int, ephemeral: bool = False):
        try:
            old: SimpleReplyData = self.repl.remove_reply(alias, index)
        except ValueError:
            await self.client.user_feedback(interaction, title='Reply deletion failed',
                                            desc='The given alias does not exist.', ephemeral=ephemeral)
            return
        except IndexError:
            await self.client.user_feedback(interaction, title='Reply deletion failed', desc='Reply index out of bounds',
                                            ephemeral=ephemeral)
            return

        await self.logger.delete_reply(interaction, alias, old) # FIXME: not passing data!
        await self.client.user_feedback(interaction, title='Reply deleted successfully', ephemeral=ephemeral)

    # region autocomplete
    @create_reply.autocomplete('alias')
    @edit_reply.autocomplete('alias')
    @delete_reply.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str):
        target = current.lower()  # Prevent repeat transformation
        aliases: list[SimpleAliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]

    @edit_reply.autocomplete('index')
    @delete_reply.autocomplete('index')
    async def _index_options_autocomplete(self, interaction: discord.Interaction, current: int) -> list[Choice[int]]:
        alias = interaction.namespace.alias
        if not alias:
            return []
        # Try and find the current alias.
        if not self.repl.alias_exists(alias):
            return [Choice(name='Bad alias.', value=-1)]
        replies: list[SimpleReplyData] = self.repl.get_replies_by_alias(alias)
        # Time to compress this stuff.
        lower, upper = cram_options(len(replies), current, 4, favour='higher')
        return [
            # Offset like this because indexing is by 1 for users.
            Choice(name=f'{offset + 1} ({reply.type}): {reply.data[:80]}', value=offset + 1)
            for offset, reply in enumerate(replies[lower:upper])
        ]
    # endregion

async def attach_cogs(client: BotClient, repl: GlobalTextAutorepliesInterface, logger: GlobalLogger):
    await client.add_cog(_AliasGlobalAdminCog(client, repl, logger))
    await client.add_cog(_TriggerGlobalAdminCog(client, repl, logger))
    await client.add_cog(_ReplyGlobalAdminCog(client, repl, logger))