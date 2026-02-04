from Rewrite.variables_parser import parse_variables
from Rewrite.variables_parser.instructionexecutor import *

import asyncio

fact: str = 'This is a fact with {user} in it.'
output: list[Instruction] = parse_variables(fact)
for i in output:
    print(i)

executor: DebugInstructionExecutor = DebugInstructionExecutor(BotClient())
asyncio.run(executor.run(output, interaction=DebugInteraction()))
print(executor.output)