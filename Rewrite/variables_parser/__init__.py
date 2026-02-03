from __future__ import annotations
from enum import Enum
import datetime as _datetime
import re as _re

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
LEGAL_VARIABLE_NAME_CHARACTERS: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'
SLEEP_TIMER_UPPER_BOUND: float = 3600 # in seconds
SLEEP_TIMER_LOWER_BOUND: float = 0.25

class InstructionParseError(CustomDiscordException):
    def __init__(self, bad_var: str, reason: str = None, refer_wiki: bool = True):
        self.bad_var: str = bad_var
        self.reason: str = reason
        super().__init__(f'Could not parse **{bad_var}**{f"\n**Reason:**\n{reason}" if reason else ""}', refer_wiki=refer_wiki)

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
    # f: floating point, supported using . as decimal point (I am european and use , all the time but it's also a variable separator so who gives)
    # s: string, optional options/max length
    # i: Parsable instructions. May include regular text and need their own escaping symbols.

    # Active actions
    PUSH = -1  # push(n[0,1,2] = 0) ; n: pingable: 0: None, 1: Interaction author, 2: All ; send built output.
    SLEEP = -2 # sleep(f = 1) ; Async sleep execution for f seconds. f max decimals = 2
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
    def from_string(build: str, depth: int = 0, memstack: list[dict[str, type]] = None) -> list[Instruction]:
        """
        Determines instruction type(s) and creates instructions using their parameters.
        :param build: Input string
        :param depth: The current recursion depth, in case a sub-instruction requires recursion.
        :param memstack: The memory stack, layered on scope, of the current scope. Defines variable types for type checking.
        :return: Instructions from Build
        """
        if depth > MAX_RECURSION_DEPTH:
            raise InstructionParseError(build,'Maximum recursion depth exceeded. Lower the complexity of your input.')

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
                # inside of (i*) arguments of some function. required for, for example, Writing compat. fixme: figure this out properly.
                if len(layer_stack) > 0 and layer_stack[-1] == '(':
                    subbuild += char
                if len(layer_stack) == 0:
                    subsections.append(subbuild.strip())
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
            subsections.append(subbuild.strip())
        # Step 2: Go through individual instructions and see if they are valid. If so, append them to the result output.

        instructions: list[Instruction] = []
        mem: dict[str, type] = {} # local memory
        memstack = [INITIAL_MEMORY_TYPES.copy()] if not memstack else memstack + [mem]

        def fetch(key: str) -> type | None:
            _mem: dict[str, ...] = {}
            for frame in reversed(memstack):
                for k, v in frame.items():
                    _mem[k] = v
            return _mem[key] if key in mem.keys() else None

        def assign(key: str, val: type):
            assigned: bool = False
            for _frame in memstack:
                if key in _frame.keys():
                    _frame[key] = val
                    assigned = True
                    break
            if not assigned:
                mem[key] = val

        i = 0
        while i < len(subsections):
            subsection = subsections[i]

            # Case 1: mem access for Build instruction.
            if fetch(subsection) is not None:
                if i < len(subsections) - 1:
                    raise InstructionParseError(subsection, f'Encountered BUILD Instruction before end of block.\n'
                                                            f'Position: **{i}**. Expected: **{len(subsections)}**.\n'
                                                            f'In block {build}\n'
                                                            f'\n'
                                                            f'To fix: Move your BUILD instruction to the end of your block. Blocks cannot contain more than one BUILD instruction to force you to format. Open a new block to include a new BUILD instruction.')
                else:
                    instructions.append(Instruction(InstructionType.BUILD, content=subsection)) # can be used regardless of type.
            # Case 2: Instruction is of one of the predefined functions, incompatible with comprehensions.
            # Defining regex for each specified syntax up above.
            # PUSH = push(n[0,1,2] = 0) ; n: pingable: 0: None, 1: Interaction author, 2: All ; send built output.
            # SLEEP = sleep(n = 1) ; Async sleep execution for n seconds.
            # WRITING = writing(*i) ; async with message.channel.typing(): {i}

            SLEEP_CONST = _re.match(r'sleep\((?P<time>(\d{1,4}(\.\d{1,2})?)?)\)', subsection) # a.bc digits, a mandatory, .b option if a, c option if b, up to 2 digit decimal
            SLEEP_CONST_MATCH = SLEEP_CONST is not None
            SLEEP_VAR = _re.match(rf'sleep\((?P<time>([{LEGAL_VARIABLE_NAME_CHARACTERS}]+))\)', subsection) # just taking contents if they consist of characters to try memory.

            PUSH_CONST = _re.match(r'push\((?P<pingable>(\d?))\)', subsection)  # digit 0,1,2, default to 0
            PUSH_CONST_MATCH = PUSH_CONST is not None
            PUSH_VAR = _re.match(rf'push\((?P<pingable>([{LEGAL_VARIABLE_NAME_CHARACTERS}]+))\)', subsection) # check for var.

            WRITING = _re.match(r'writing\((?P<instr>(.*))\)', subsection) # just extract and see if output has at least one instruction.

            if SLEEP_CONST_MATCH:
                time = SLEEP_CONST.group('time')
                if not time:  # default value use as no parameter was passed in
                    instructions.append(Instruction(InstructionType.SLEEP, time=1))
                    continue
                try:
                    time = float(time)
                    if time < SLEEP_TIMER_LOWER_BOUND:
                        raise InstructionParseError(subsection, 'SLEEP Instruction time is below lower bound.\n'
                                                                f'Received: **{time}**. Minimal: **{SLEEP_TIMER_LOWER_BOUND}**')
                    elif time > SLEEP_TIMER_UPPER_BOUND:
                        raise InstructionParseError(subsection, f'SLEEP Instruction time exceeds upper bound.\n'
                                                                f'Received: **{time}**. Maximum: **{SLEEP_TIMER_UPPER_BOUND}**.')
                    instructions.append(Instruction(InstructionType.SLEEP, time=time))
                    continue
                except ValueError:
                    SLEEP_CONST_MATCH = False
            if not SLEEP_CONST_MATCH and SLEEP_VAR:
                time = SLEEP_VAR.group('time')
                # Check memory
                val = fetch(time)
                if not val:
                    raise InstructionParseError(subsection, f'Could not find time variable \'{time}\' in memory.')
                if not val in [float, int]:
                    raise InstructionParseError(subsection, f'SLEEP Instruction requires parameter of type **float** or **int**, received **{time}** of type **{val}**.')
                instructions.append(Instruction(InstructionType.SLEEP, time=time))
                continue

            if PUSH_CONST_MATCH:
                pingable = PUSH_CONST_MATCH.group('pingable')
                if not pingable:
                    instructions.append(Instruction(InstructionType.PUSH, pingable=MentionOptions.NONE))
                    continue
                try:
                    pingable_val = int(pingable)
                except ValueError:
                    raise InstructionParseError(subsection, f'Could not parse {pingable} into an Integer.')
                if not pingable_val in [0, 1, 2]:
                    raise InstructionParseError(subsection, f'Pingable option **{pingable_val}** not in **[0, 1, 2]**.')
                pingable: MentionOptions
                if pingable_val == 0:
                    pingable = MentionOptions.NONE
                elif pingable_val == 1:
                    pingable = MentionOptions.AUTHOR
                elif pingable_val == 2:
                    pingable = MentionOptions.ALL

                instructions.append(Instruction(InstructionType.PUSH, pingable=pingable))
                continue





        # Default
        return [Instruction(InstructionType.BUILD, content='{ Instruction of unknown type failed Parsing: \'' + build + '\'}'),] if not instructions else instructions

def parse_variables(parse_string: str, depth: int = 0, *args, **kwargs) -> list[Instruction]:
    # To prevent infinite recursion but also limit memory usage, install a max depth limit. TODO: configurable.
    # Anyways, what is the fallback in case max depth is reached?

    # make sure to create an instruction to send at the end, but not after other non-message things.
    # precompute memory usage if possible to set an upper limit.
    if depth > MAX_RECURSION_DEPTH:
        raise InstructionParseError(parse_string, 'Maximum recursion depth exceeded. Lower the complexity of your input.')

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