from Rewrite.variables_parser import parse_variables
from Rewrite.variables_parser.instructionexecutor import *

import asyncio

fact: str = 'This is a fact with {user} in it.'
output: list[Instruction] = parse_variables(fact)
for i in output:
    print(i)

executor: DebugInstructionExecutor = DebugInstructionExecutor(BotClient(None, None))
asyncio.run(executor.run(output, interaction=None))
print(executor.output)