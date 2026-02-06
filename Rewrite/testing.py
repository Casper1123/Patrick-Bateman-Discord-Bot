from Rewrite.variables_parser import parse_variables
from Rewrite.variables_parser.instructionexecutor import *

import asyncio

fact1: str = 'This is a fact with {guild.id} in it as well as a writing block.{writing(sleep(); push(1))}Isn\'t it awesome?!'
fact2: str = 'opt {choice(\'First Option\', \'Second Option\', \'Third option: {self}\')}'
fact3: str = 'This fact has a random user in it: {tru(0)}'
output: list[Instruction] = parse_variables(fact2)
for i in output:
    print(i)

executor: DebugInstructionExecutor = DebugInstructionExecutor(BotClient(None, None), pure_output=False)
asyncio.run(
    executor.run(output, interaction=None)
)
print(executor.output)