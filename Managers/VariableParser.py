import random as _rd
import re as _re

import discord
from discord.ext import commands

from .Exceptions import FactIndexError
from .FactsManager import FactsManager

def process_variables(fact: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                 bot: commands.Bot) -> str:
    return process_fact(fact, facts_manager, interaction, bot)

def process_fact_cvar(variable: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                 bot: commands.Bot, shuffled_memlist: list[discord.Member] | None = None) -> str:
    if not variable.endswith(')'):
        return "{" + variable + "}"
    variable = variable.removesuffix('fact(').removesuffix(")")
    if not variable:
        return facts_manager.get_fact(interaction.guild_id, None)

    try:
        num = int(variable)
    except ValueError:  # Unfortunately cannot just regex this as easily. Seems you cannot just.. have multiple function calls inside boowomp.
        try:
            # Try parsing it as a variable.
            num = int(process_variable(variable, facts_manager, interaction, bot, shuffled_memlist))
        except ValueError:
            return "{" + variable + "}"
    try:
        return facts_manager.get_fact(interaction.guild_id, num)
    except FactIndexError as e:
        return "{" + f"fact index error; index {e.index}" + "}"

def process_tranduser(op: str, num: int, shuffled_memlist: list[discord.Member]) -> str:
    # pattern = r"^tru_(?P<op>\w+)\((?P<num>-?\d+)\)$"  # starts with tru, gets some op chars till (, then some optionally neg digits and then checks for string end.
    num = int(num) % len(shuffled_memlist)  # Standardise into a member index.
    member: discord.Member = shuffled_memlist[num]

    op_dict = {
        "acc": member.name,
        "id": member.id,
        "name": member.display_name,
    }
    try:
        return op_dict[op]
    except KeyError:
        return "{invalid tru operation.}"

def process_choice(variable: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                   bot: commands.Bot, shuffled_memlist: list[discord.Member] | None) -> str:
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
        return process_fact(_rd.choice(choices), facts_manager, interaction, bot, shuffled_memlist)
    except IndexError:
        return "{choice:}"


def process_variable(variable: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                     bot: commands.Bot, shuffled_memlist: list[discord.Member] | None) -> str:
    if isinstance(interaction, discord.Interaction):
        user = interaction.user
    else:
        user = interaction.author

    guild = interaction.guild
    channel = interaction.channel
    in_server: bool = guild is not None
    random_user: discord.Member = None if not in_server else _rd.choice(guild.members)

    # fact counts
    local_fact_count: int = len(facts_manager.get_facts(guild.id))
    global_fact_count: int = len(facts_manager.get_facts(None))
    # Information available in DMs
    dm_var_dict: dict = {
        "user.account": user.name,
        "user.id": user.id,
        "user.name": user.display_name,

        "total_facts": str(global_fact_count + local_fact_count),
        "global_facts": str(global_fact_count),
        "local_facts": str(local_fact_count),
        "enter": "\n",

        "self.name": bot.user.name,
        "self.id": bot.user.id,
    }

    # Information available in servers
    guild_var_dict: dict = {
        "randomuser.account": random_user.name,  # Deprecated, use tru instead.
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
    # Rand
    match = _re.match(r"^rand\((?P<a>-?\d+), (?P<b>-?\d+)\)$", variable)
    if match:
        try:
            a = int(match.group("a"))
            b = int(match.group("b"))
        except ValueError:
            return "{" + variable + "}"

        if a < b:
            return str(_rd.randint(a, b))
        else:
            return "{a >= b}"

    # tru
    match = _re.match(r"^tru_(?P<op>\w+)\((?P<num>-?\d+)\)$", variable)
    if match:
        return process_tranduser(match.group("op"), match.group("num"), shuffled_memlist)

    # choice
    if variable.startswith("choice:"):
        return process_choice(variable, facts_manager, interaction, bot, shuffled_memlist)

    # fact
    if variable.startswith("fact("):
        return process_fact_cvar(variable, facts_manager, interaction, bot, shuffled_memlist)

    return "{" + variable + "}"  # Ugly concatenation because f"" wouldn't work with \{


def process_fact(fact: str, facts_manager: FactsManager, interaction: discord.Interaction | discord.Message,
                      bot: commands.Bot, shuffled_memlist: list[discord.Member] | None = None) -> str:

    if shuffled_memlist is None and interaction.guild is not None and fact.__contains__("{tru_"):
        shuffled_memlist = [i for i in interaction.guild.members]
        _rd.shuffle(shuffled_memlist)

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
                result += str(process_variable(current_variable, facts_manager, interaction, bot, shuffled_memlist))  # Append current 'result' string after process with current variable contents.
                current_variable = ""  # reset
                continue

        if opened:
            current_variable += char
        else:
            result += char

    result += "{" + current_variable if current_variable != "" else ""  # Handle unhandled leftovers.

    return result.replace("\\n", "\n")  # replacing the only non-variable thing
