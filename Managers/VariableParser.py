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
    # Example of a choice:
    # {choice:"a","b","c"}. Quotes and spaces mandatory.
    choices: list[str] = []
    opened: bool = False
    var_opened: int = 0
    current_choice: str = ""
    valid_boundaries = ["'", '"']

    variable = variable.removeprefix("choice:")  # "{choice:"a","b"}","a"
    # detect if current choice has an opened variable and close it only when that variable is done.

    for i, char in enumerate(variable):
        # First character, has to be ", if it's not then... that's a mistake. At least one choice has to be given.
        if i == 0 and char not in valid_boundaries:
            return "{choice:}"
        elif i == 0 and char in valid_boundaries:  # If the first character is an opening boundary, then we're good.
            opened = True
            continue  # Next char

        # Handle subsequent characters
        # First, we check for a non-excluded variable opening or closing character.
        if char == "{" and variable[i - 1] != "\\":
            var_opened += 1
            current_choice += char
            continue
        elif char == "}" and variable[i - 1] != "\\":
            var_opened -= 1
            current_choice += char
            continue

        # Variables checked, now for the regular; if we're in a variable, we want to take all the characters.
        # If we are not, we check for an ending.
        if var_opened > 0:
            current_choice += char
            continue

        if opened:
            if char in valid_boundaries and variable[i - 1] != "\\":  # it's a valid escape character.
                opened = False
                choices.append(current_choice)
                current_choice = ""
                continue
            # If it's not a valid escape character, append character
            current_choice += char
        else:
            # Continue until finding a valid opening character.
            if char in valid_boundaries and variable[i - 1] != "\\":
                opened = True

    # Add leftovers if their choice wasn't finished.
    if current_choice != "":
        choices.append(current_choice)

    # Recursively process the choice.
    try:
        return process_fact(_rd.choice(choices), facts_manager, interaction, bot)
    except IndexError:
        return "{choice:}"


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
        "global_facts": str(len(facts_manager.get_facts(guild.id, separate=True)[0])),
        "local_facts": str(len(facts_manager.get_facts(guild.id, separate=True)[1])),
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

        "owner.id": guild.owner,
        "owner.name": guild.owner.display_name,
        "owner.account": guild.owner.name,

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
    opened: int = 0  # counts opening curly-brackets.
    for i, char in enumerate(fact):
        # Go through chars and try to separate out any variables.
        if char == "{":
            if i == 0:  # cannot have suffix @ i = 0
                opened += 1
                continue
            if fact[i - 1] != "\\":  # Separation to not try to access fact[-1] which is impossible.
                if opened > 0:
                    current_variable += char  # Add curly to current variable if already opened, but expects it to be closed as it wasn't a \"
                opened += 1
                continue

        if char == "}" and opened > 0:
            if fact[i - 1] != "\\":
                opened -= 1
            if opened == 0:
                result += str(process_variable(current_variable, facts_manager, interaction, bot))  # Append current 'result' string after process with current variable contents.
                current_variable = ""  # reset
                continue

        if opened:
            current_variable += char
        else:
            result += char

    result += "{" + current_variable if current_variable != "" else ""  # Handle unhandled leftovers.

    return result.replace("\\n", "\n")  # replacing the only non-variable thing
