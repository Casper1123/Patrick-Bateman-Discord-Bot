import asyncio

from piss.executing.test import TestInstructionExecutor
from piss.instructions.abstract import Instruction
from piss.parsing import parse_instructions_from_string

if __name__ != '__main__':
    raise ImportError('Do not import this file, only run it.')
    # Do not want to trigger the input statement below and halting the process.

txt: str = input('Enter PISS data: ')
parsed: list[Instruction] = parse_instructions_from_string(txt)
executor: TestInstructionExecutor = TestInstructionExecutor()

asyncio.run(executor.run(parsed))