import asyncio

from piss.instructions.abstract import Instruction
from piss.parsing import parse_instructions_from_string
from piss.executing.test import TestInstructionExecutor

if __name__ != '__main__':
    raise ImportError('Do not import this file, only run it.')

txt: str = input('Enter PISS data: ')
parsed: list[Instruction] = parse_instructions_from_string(txt)
executor: TestInstructionExecutor = TestInstructionExecutor()

asyncio.run(executor.run(parsed))