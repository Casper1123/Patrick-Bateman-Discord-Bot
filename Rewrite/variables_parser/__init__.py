from __future__ import annotations
from enum import Enum
import datetime as _datetime

from Rewrite.utilities.exceptions import CustomDiscordException

INITIAL_MEMORY_TYPES: dict[str, type] = {
                '\\n': str,

                # interaction target
                'user.id': int,
                'user': str,
                'user.name': str,
                'user.created_at': _datetime.datetime,
                'user.account': str,
                'user.status': str,
                'user.mutual_guilds': int,
                'user.roles': int,  # role count, not the actual roles.

                'self.id': int,
                'self': str,
                'self.name': str,
                'self.created_at': _datetime.datetime,
                'self.account': str,
                'self.roles': int,

                'channel': str,
                'channel.id': int,
                'channel.name': str,
                'channel.created_at': _datetime.datetime,
                'channel.jump_url': str,

                'guild': str,
                'guild.id': int,
                'guild.name': str,
                'guild.created_at': _datetime.datetime,
                'guild.members': int, # member count
                'guild.roles': int, # still, role count.

                # guild owner
                'owner.id': int,
                'owner': str,
                'owner.name': str,
                'owner.created_at': _datetime.datetime,
                'owner.account': str,
                'owner.roles': int,

                'message': int,
                'message.jump_url': str,
            }


class InstructionParseError(CustomDiscordException):
    def __init__(self, bad_var: str, reason: str = None):
        self.bad_var: str = bad_var
        self.reason: str = reason
        super().__init__(f'Could not parse **{bad_var}**{f"\n**Reason:** {reason}" if reason else ""}')

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

        # Step 1: separate into instruction subsections.
        bounds: list[str] = ['{', '[', '(', '\''] # Opens another subsection. Input is already stripped of containing {}
        be_map: dict[str, str] = { '{': '}', '[': ']', '(': ')', '\'': '\''}
        escapes: list[str] = list(be_map.values())  # convert to list, makes it easier to work with.
        layer_stack: list[str] = []  # Keeps track of layers open as we need to distinguish in characters here.
        subsections: list[str] = []  # Keep track of every single operation, separated by ; terminator.
        subbuild: str = ''
        terminator: str = ';'

        i: int = 0
        while i < len(build):
            char: str = build[i]
            # we are inside a string.
            in_string: bool = layer_stack and layer_stack[-1] == '\''
            # escaped character
            escaped: bool = i > 0 and build[i-1] == '\\'

            # case 1: character is escaped
            if escaped:
                subbuild += char
            elif char == terminator:
                if len(layer_stack) == 0:
                    subsections.append(subbuild)
                    subbuild = ''
                else:
                    expected: list[str] = [be_map[layer_stack[i]] for i in range(len(layer_stack))]  # running into some typing issues so this is the ugly version
                    raise InstructionParseError(subbuild + char,
                        reason='Non-escaped terminator appeared before frame stack end (expected the following escaping characters, in order): ' + ''.join(expected))
            elif char in bounds:
                subbuild += char
                layer_stack.append(char)
            elif char in escapes:
                top = layer_stack[-1]
                top_escape = be_map[top]
                if char == top_escape:
                    subbuild += char
                    layer_stack.pop()
                else:
                    raise InstructionParseError(subbuild + char, reason=f'Encountered unescaped {char} before encountering {top_escape}')
            else:
                subbuild += char
            i += 1
        if len(layer_stack) > 0:
            expected: list[str] = [be_map[layer_stack[i]] for i in range(len(layer_stack))]  # running into some typing issues so this is the ugly version
            raise InstructionParseError(subbuild, reason='Reached end-of-line before closure of frame stack. Expected the following characters before termination: ' + ''.join(expected))
        else:
            subsections.append(subbuild)
            subbuild = '' # just in case.

        # Step 2: Go through individual instructions and see if they are valid. If so, append them to the result output.
        instructions: list[Instruction] = []
        for instruction in subsections:
            ...



        # Default
        return [Instruction(InstructionType.BUILD, content='{ Instruction of unknown type failed Parsing: \'' + build + '\'}'),] if not instructions else instructions

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