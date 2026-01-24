from __future__ import annotations
from enum import Enum

import discord
from discord.ext import commands

from Rewrite.utilities.exceptions import CustomDiscordException

# todo: move to config, somehow.
MAX_RECUSION_DEPTH = 5


class InstructionType(Enum):
    # Active actions
    PUSH = -1  # send built output.
    SLEEP = -2
    WRITING = -3  # async with message.channel.typing(): {}

    # Primary text
    BUILD = 0 # basic instruction, append content to next message.
    BASIC_REPLACE = 2  # basic data replacement. Takes in a single argument, which is the key to the dictionary.

    # Can involve memory
    DEFINE = 50 # define new var or overwrite value of.
    # SUM, SUB, *, /, //, %, ^, ( parenthesis ), log.
    # matrices? function definitions?
    # iterative sum, mult, etc?
    # random number or something

    RANDOMUSER = 25  # TRU - True Random User, todo: port this over.
    CHOICE = 26
    FACT = 27  # fact(index) call. Do push in depth!
        # todo: figure out better numbering

# fixme: unsupported: total_facts, global_facts, local_facts
class BasicReplaceOptions(Enum):
    NEWLINE = -1

    # interaction target
    USERACCOUNT = 0
    USERID = 1
    USERNAME = 2

    # self
    NAME = 3
    ID = 4
    NICK = 5

    # location
    CHANNEL = 6
    CHANNELID = 7

    GUILD = 8
    GUILDID = 9
    GUILDDATE = 10 # created_at

    # guild.owner
    OWNER = 11
    OWNERID = 12


class Instruction:
    def __init__(self, instruction_type: InstructionType, **options):
        raise NotImplementedError()
        self.type: InstructionType = instruction_type
        self.options: dict[str, object] = options  # todo: define exact types allowed to be saved.

    @staticmethod
    def from_string(build: str, depth: int = 0) -> list[Instruction]:
        """
        Determines instruction type(s) and creates instructions using their parameters.
        :param build: Input string
        :param depth: The current recusion depth, in case a sub-instruction requires recursion.
        :return: Instructions from Build
        """
        raise NotImplementedError()
        # note: use Regex to pattern match if possible. Should be easy, no?
        # how the fuck does one do c := a + b
        # --> check for memory references too, though that example was supposed to be 'how do I parse stuff'


class ParsedExecutionFailure(CustomDiscordException):
    def __init__(self, instruction: Instruction, cause: Exception | None = None) -> None:
        super().__init__(f'Failed to execute Instruction of type **{instruction.type}** given options \'{instruction.options}\'', cause)



class ParsedVariables:
    def __init__(self, instructions: list[Instruction]):
        self._instructions: list[Instruction] = instructions # Note to self on how this could be done

    async def run(self, client: commands.Bot, interaction: discord.Interaction | discord.Message):
        # TODO: make fail if not ran in guild context. Do not let DM context make things more complicated. Get this to work first.
        async def send_output(out: str):
            ... # todo: implement sending data.
            if out == "": out = "{ ? Empty output string ? }" # cannot send empty data. Substituting to allow for debugging.

        raise NotImplementedError() # Runs stored instructions in sequence.
        i: int = 0
        build: str = "" # expanded until finished or message sends, then reset.
        mem: dict[str, ...] = {}
        while i < len(self._instructions):
            instruction = self._instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    # todo: settings for message. Assuming it's sent right now.
                    await send_output(build)
                    build = ""
                elif instruction.type == InstructionType.DEFINE:
                    mem[instruction.options['name']] = instruction.options['content']
                else:
                    build += '{ Skip exec of type ' + instruction.type + '; NotImplemented }'
            except Exception as e:
                raise ParsedExecutionFailure(instruction, cause=e)
            i += 1
        if build:
            await send_output(build)


    def parse_raw(self, parse_string):
        raise NotImplementedError() # Parses raw into itself.

def parse_variables(parse_string: str, depth: int = 0, *args, **kwargs) -> ParsedVariables:
    raise NotImplementedError() # todo: implement parser.
    # To prevent infinite recursion but also limit memory usage, install a max depth limit. TODO: configurable.
    # Anyways, what is the fallback in case max depth is reached?

    # make sure to create an instruction to send at the end, but not after other non-message things.
    # precompute memory usage if possible to set an upper limit.
    if depth > MAX_RECUSION_DEPTH:
        return ParsedVariables([Instruction(InstructionType.BUILD, content='{ Maximum recursion depth reached. }')])

    # Iterate through string, take out {} and send contents inside to Instruction parser.
    instructions: list[Instruction] = []
    i: int = 0
    build: str = ""
    depth: int = 0 # count opened brackets. We consider the var closed when back to 0.
    while i < len(parse_string):
        char: str = parse_string[i]

        if char == "{":
            if parse_string[i-1] == '\\' and i > 0: # ensure doesn't check end of string but char in front
                build += char
            elif i == 0 or parse_string[i-1] != '\\' and build:  # In a variable now. Previous build needs to be exited.
                instructions.append(Instruction(InstructionType.BUILD, content=build))
                build = ""
                depth += 1
                continue
        elif char == "}":
            if parse_string[i-1] == '\\':
                build += char
            else:
                depth -= 1

            if depth == 0:
                instructions += Instruction.from_string(build, depth=depth)
                build = ""
                continue
        else:
            build += char