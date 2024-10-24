import random as _rd

import discord
from discord.ext import commands

from .FactsManager import FactsManager


def process_rand(variable: str) -> str:
    try:
        lower, upper = [int(i) for i in variable.removeprefix("rand:").split(",")]
    except ValueError:
        return "{" + variable + "}"

    try:
        return str(_rd.randint(lower, upper))
    except ValueError:
        return "{" + variable + "}"


def process_choice(variable: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                   bot: commands.Bot) -> str:
    choices: list[str] = []
    opened: bool = False
    current_choice: str = ""

    variable = variable.removeprefix("choice:")
    for i, char in enumerate(variable):
        if char == "\"" and not opened:  # If not opened, open if it's a valid opener.
            if i == 0:
                opened = True
                continue
            elif variable[i - 1] != "\\":
                opened = True
                continue
        if char == "\"" and opened:  # If it's opened, close it if it's a valid closer.
            if variable[i - 1] != "\\":
                opened = False
                choices.append(current_choice)
                current_choice = ""
                continue

        if opened:
            current_choice += char
        # else: add it to.. what?

    if not choices:
        return "{" + variable + "}"

    # todo: fix 'no option' and 'stacking choices'

    # Recursively process the choice.
    return process_fact(_rd.choice(choices), facts_manager, interaction, bot)


def process_variable(variable: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                     bot: commands.Bot) -> str:
    if isinstance(interaction, discord.Interaction):
        user = interaction.user
    else:
        user = interaction.author

    guild = interaction.guild
    channel = interaction.channel
    in_server: bool = guild is not None
    random_user: discord.Member = None if not in_server else _rd.choice(guild.members)

    # Information available in DMs
    dm_var_dict: dict = {
        "user.account": user.name,
        "user.id": user.id,
        "user.name": user.display_name,

        "total_facts": str(len(facts_manager.get_facts(guild.id))),
        "global_facts": str(len(facts_manager.get_facts(guild.id, seperate=True)[0])),
        "local_facts": str(len(facts_manager.get_facts(guild.id, seperate=True)[1])),
        "enter": "\n",

        "self.name": bot.user.name,
        "self.id": bot.user.id,
    }
    
    # Information available in servers
    guild_var_dict: dict = {
        "randomuser.account": random_user.name,
        "randomuser.id": random_user.id,
        "randomuser.name": random_user.display_name,

        "channel.name": channel.name,
        "channel.id": channel.id,

        "guild.name": guild.name,
        "guild.created_at": guild.created_at,
        "guild.id": guild.id,

        "guild.owner.id": guild.owner,
        "guild.owner.name": guild.owner.display_name,
        "guild.owner.account": guild.owner.name,

        "self.nick": guild.me.nick,
    }

    # Variables
    if variable in dm_var_dict.keys():
        return dm_var_dict[variable]
    if variable in guild_var_dict.keys() and in_server:
        return guild_var_dict[variable]

    # Command Variables
    if variable.startswith("rand:"):
        return process_rand(variable)
    elif variable.startswith("choice:"):
        return process_choice(variable, facts_manager, interaction, bot)

    return "{" + variable + "}"  # Ugly concatenation because f"" wouldn't work with \{


def process_fact(fact: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                 bot: commands.Bot) -> str:
    result: str = ""
    current_variable = ""
    opened: int = 0  # determines whether it's actively processing a variable.
    for i, char in enumerate(fact):
        # Go through chars and try to separate out any variables.
        if char == "{":
            if i == 0:  # cannot have suffix @ i = 0
                opened += 1
                continue
            if fact[i - 1] != "\\":  # Separation to not try to access fact[-1] which is impossible.
                if opened > 0:
                    current_variable += char
                opened += 1
                continue

        if char == "}" and opened > 0:
            if fact[i - 1] != "\\":
                opened -= 1
            if opened == 0:
                result += str(process_variable(current_variable, facts_manager, interaction, bot))
                current_variable = ""
                continue

        if opened:
            current_variable += char
        else:
            result += char

    result += "{" + current_variable if current_variable != "" else ""  # Handle unhandled leftovers.

    return result.replace("\\n", "\n")  # replacing the only non-variable thing
