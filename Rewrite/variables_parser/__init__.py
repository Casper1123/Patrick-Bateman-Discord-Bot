from __future__ import annotations
from enum import Enum



# todo: move to config, somehow.
MAX_RECURSION_DEPTH = 5


class InstructionType(Enum):
    # fixme: unsupported: total_facts, global_facts, local_facts
    # todo: implement math,
    # todo: implement conditional branches

    # Syntax descriptors:
    # a: any of the below
    # [a, ...]: a (limited) set of option types
    # *a: any (including none at all) number of parameters
    # a = ... : Default value, making parameter optional
    # b: boolean, 0, 1, t, f
    # n: natural number, optional range
    # s: string, optional options/max length
    # i: Parsable instructions. May include regular text and need their own escaping symbols.

    # Active actions
    PUSH = -1  # send(n[0,1,2] = 0) ; n: pingable: 0: None, 1: Interaction author, 2: All ; send built output.
    SLEEP = -2 # sleep(n = 1) ; Async sleep execution for n seconds.
    WRITING = -3  # writing(*i) ; async with message.channel.typing(): {i}

    # Primary text
    BUILD = 0 # Not directly callable ; basic instruction, append content to next message.
    BASIC_REPLACE = 2  # Callable by calling an unknown instruction who's key is known by the memory ;

    # Can involve memory
    DEFINE = 50 # define new var or overwrite value of.
        # THINK ABOUT MULTIVARIABLE DEFINITION a, b := c, d !!!
    # todo: how the fuck do I fetch a value from this properly?
    # SUM, SUB, *, /, //, %, ^, ( parenthesis ), log.
    # matrices? function definitions?
    # iterative sum, mult, etc?
    # random number or something
    CALCULATE = 51

    RANDOMUSER = 25  # TRU - True Random User, todo: port this over.
    CHOICE = 26 # choice('i', 'i', *('i') ; Options i, where the first two are mandatory.  Enclosed in ' or ".
    FACT = 27  # fact(n = None) ; n: index, can be left out for truly random.
        # todo: figure out better numbering

class MentionOptions(Enum):
    NONE = 0
    AUTHOR = 1
    ALL = 2

class BasicReplaceOptions(Enum):
    # fixme: remove this entirely. Might as well use mem keys directly who cares about this. Prepare the right mem keys though.
    # annotation describes key.
    MEMORY = -2 # index key directly
    NEWLINE = -1 # nl

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
        self.type: InstructionType = instruction_type
        self.options: dict[str, object] = options  # todo: define exact types allowed to be saved.

    def __str__(self):
        return str(self.type) + ": " + str(self.options)

    @staticmethod
    def from_string(build: str, depth: int = 0) -> list[Instruction]:
        """
        Determines instruction type(s) and creates instructions using their parameters.
        :param build: Input string
        :param depth: The current recursion depth, in case a sub-instruction requires recursion.
        :return: Instructions from Build
        """
        # note: use Regex to pattern match if possible. Should be easy, no?
        # how the fuck does one do c := a + b
        # --> check for memory references too, though that example was supposed to be 'how do I parse stuff'

        # Case 1: Easy substitution.
        # todo: cannot have more than one of these in a single block, so make sure to write a proper error for it.


        # Default
        return [Instruction(InstructionType.BUILD, content='{ Instruction of unknown type failed Parsing: \'' + build + '\'}'),]

def parse_variables(parse_string: str, depth: int = 0, *args, **kwargs) -> list[Instruction]:
    # To prevent infinite recursion but also limit memory usage, install a max depth limit. TODO: configurable.
    # Anyways, what is the fallback in case max depth is reached?

    # make sure to create an instruction to send at the end, but not after other non-message things.
    # precompute memory usage if possible to set an upper limit.
    if depth > MAX_RECURSION_DEPTH:
        return [Instruction(InstructionType.BUILD, content='{ Maximum recursion depth reached. }')]

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

    return instructions