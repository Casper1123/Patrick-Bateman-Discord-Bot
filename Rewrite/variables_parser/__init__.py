from enum import Enum

class InstructionType(Enum):
    MESSAGE = 0 # send built output.

    DEFINE = 1 # define new var or overwrite value of.


    # SUM --> appended to built output

class Instruction:
    def __init__(self, instruction_type: InstructionType, **options):
        raise NotImplementedError()
        self.type: InstructionType = instruction_type
        self.options: dict[str, object] = options  # todo: define exact types allowed to be saved.



class ParsedVariables:

    def __init__(self):
        raise NotImplementedError()
        self._instructions: list[Instruction] = [] # Note to self on how this could be done

    async def run(self):
        async def send_output(out: str):
            ... # todo: implement sending data.
            if out == "": out = "{ ? Empty output string ? }" # cannot send empty data. Substituting to allow for debugging.

        raise NotImplementedError() # Runs stored instructions in sequence.
        i: int = 0
        build: str = "" # expanded until finished or message sends, then reset.
        mem: dict[str, ...] = {}
        while i < len(self._instructions):
            instruction = self._instructions[i]

            if instruction.type == InstructionType.MESSAGE:
                # todo: settings for message. Assuming it's sent right now.
                await send_output(build)
                build = ""
            elif instruction.type == InstructionType.DEFINE:
                # assuming setting TODO: finish
                name: str
                value: object
                mem[name] = value

            i += 1


    def parse_raw(self, parse_string):
        raise NotImplementedError() # Parses raw into itself.

def parse_variables(parse_string: str, depth: int = 0, *args, **kwargs) -> ParsedVariables:
    raise NotImplementedError() # todo: implement parser.
    # To prevent infinite recursion but also limit memory usage, install a max depth limit. TODO: configurable.
    # Anyways, what is the fallback in case max depth is reached?

    # make sure to create an instruction to send at the end, but not after other non-message things.