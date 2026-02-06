from Rewrite.variables_parser import parse_variables
from Rewrite.variables_parser.instructionexecutor import *

import asyncio

_fact: str = 'This is a fact with {user} in it as well as a writing block.{writing(sleep(); push())}Isn\'t it awesome?!'
fact: str = 'This fact has two options: {choice(\'First Option\', \'Second Option\')}'
output: list[Instruction] = parse_variables(fact)
for i in output:
    print(i)

executor: DebugInstructionExecutor = DebugInstructionExecutor(BotClient(None, None), pure_output=False)
asyncio.run(
    executor.run(output, interaction=None)
)
print(executor.output)