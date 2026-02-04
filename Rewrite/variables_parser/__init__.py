from __future__ import annotations
from enum import Enum
import datetime as _datetime
import re as _re

from Rewrite.utilities.exceptions import CustomDiscordException

# todo: move to config, somehow.
MAX_RECURSION_DEPTH = 5
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

    # external
    'local_facts': int,
    'global_facts': int,
    'total_facts': int,
}
SLEEP_TIMER_UPPER_BOUND: float = 3600 # in seconds
SLEEP_TIMER_LOWER_BOUND: float = 0.25

class InstructionParseError(CustomDiscordException):
    def __init__(self, bad_var: str, reason: str = None, refer_wiki: bool = True):
        self.bad_var: str = bad_var
        self.reason: str = reason
        super().__init__(f'Could not parse **{bad_var}**{f"\n**Reason:**\n{reason}" if reason else ""}', refer_wiki=refer_wiki)

class InstructionType(Enum):
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
    BASIC_REPLACE = 2

    RANDOMUSER = 25  # TRU - True Random User, todo: port this over.
    CHOICE = 26 # choice('i', 'i', *('i') ; Options i, where the first two are mandatory.  Enclosed in ' or ".

    LOCAL_FACTS = 28
    GLOBAL_FACTS = 29
    TOTAL_FACTS = 30
    RANDOM_REPL = 31


class MentionOptions(Enum):
    NONE = 0
    AUTHOR = 1
    ALL = 2

class Instruction:
    def __init__(self, instruction_type: InstructionType, **options):
        self.type: InstructionType = instruction_type
        self.options: dict[str, object] = options

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

        # region Step 1: separate into instruction subsections.
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
        # endregion

        # region Step 2: Instruction recognition
        instructions: list[Instruction] = []
        local_scope = memstack[-1]

        def fetch(key: str) -> type | None:
            _mem: dict[str, ...] = {}
            for frame in reversed(memstack):
                for k, v in frame.items():
                    _mem[k] = v
            return _mem[key] if key in _mem.keys() else None

        for subsection in subsections:

            # Case 1: mem access for Build instruction.
            res = fetch(subsection)
            if res is not None:
                if i < len(subsections) - 1:
                    raise InstructionParseError(subsection, f'Encountered BUILD Instruction before end of block.\n'
                                                            f'Position: **{i}**. Expected: **{len(subsections)}**.\n'
                                                            f'In block {build}\n'
                                                            f'\n'
                                                            f'To fix: Move your BUILD instruction to the end of your block. Blocks cannot contain more than one BUILD instruction to force you to format. Open a new block to include a new BUILD instruction.')
                else:
                    instructions.append(Instruction(InstructionType.BASIC_REPLACE, key=subsection)) # can be used regardless of type.
                    continue

            # Case 2: Instruction is of one of the predefined functions, incompatible with comprehensions.
            SLEEP_CONST = _re.match(r'^sleep\((?P<time>(\d{1,4}(\.\d{1,2})?)?)\)$', subsection) # a.bc digits, a mandatory, .b option if a, c option if b, up to 2 digit decimal
            if SLEEP_CONST:
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
                    raise InstructionParseError(subsection, f'Could not convert **{time}** into a number.')

            PUSH_CONST = _re.match(r'^push\((?P<pingable>(\d?))\)$', subsection)  # digit 0,1,2, default to 0
            if PUSH_CONST:
                pingable = PUSH_CONST.group('pingable')
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

            WRITING = _re.match(r'^writing\((?P<instr>(.*))\)$', subsection)  # just extract and see if output has at least one instruction.
            if WRITING:
                content = WRITING.group('instr')
                content_instr: list[Instruction] = Instruction.from_string(content, depth + 1, memstack)
                if not content_instr:
                    raise InstructionParseError(subsection, f'WRITING instruction did not receive any instructions (received **{content}**).')
                instructions.append(Instruction(InstructionType.WRITING, instructions=content_instr)) # fixme: this isn't like, safe. right?
                continue

            # todo: first version should support some form of choice, random user. Choice might want to support ' & "
            RANDOM = _re.match(r"^rand(om)?\((?P<a>-?\d+), (?P<b>-?\d+)\)$", subsection) # todo: support var
            if RANDOM:
                a = RANDOM.group('a')
                b = RANDOM.group('b')
                try:
                    a = int(a)
                except ValueError:
                    raise InstructionParseError(subsection, f'**{a}** is not a Python-recognized integer.')
                try:
                    b = int(b)
                except ValueError:
                    raise InstructionParseError(subsection, f'**{b}** is not a Python-recognized integer.')
                if a >= b:
                    raise InstructionParseError(subsection, f'**left ({a})** should not be greater than ** right ({b})**.')
                instructions.append(Instruction(InstructionType.RANDOM_REPL, lower=a, upper=b))
                continue


            # Default case, warn user of bad input.
            raise InstructionParseError(subsection, f'Instruction not recognized.')
        # endregion

        return instructions

def parse_variables(parse_string: str, depth: int = 0, memstack: list[dict[str, ...]] = None) -> list[Instruction]:
    if depth > MAX_RECURSION_DEPTH:
        raise InstructionParseError(parse_string, 'Maximum recursion depth exceeded. Lower the complexity of your input.')

    mem: dict[str, type] = INITIAL_MEMORY_TYPES.copy() if not memstack else {}  # local memory
    memstack = [mem] if not memstack else memstack + [mem]

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
        elif char == "}":
            if parse_string[i-1] == '\\':
                build += char
            else:
                depth -= 1

            if depth == 0:
                instructions += Instruction.from_string(build, depth=depth, memstack=memstack)
                build = ""
        else:
            build += char
        i += 1
    if build: instructions.append(Instruction(InstructionType.BUILD, content=build))

    return instructions