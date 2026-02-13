import asyncio

from Rewrite.variables_parser import parse_variables
from Rewrite.variables_parser.instructionexecutor import *

fact1: str = 'This is a fact with {guild.id} in it as well as a writing block.{writing(sleep(); push(1))}Isn\'t it awesome?!'
fact2: str = 'opt {choice(\'First Option\', \'Second Option\', \'Third option: {sleep(); self}\')}'
fact3: str = 'This fact has a random user in it: {tru(0)}'
fact4: str = '{choice(\'C1\', \'C2{choice("subopt1", "subopt2{choice(\'Opt1\', \'{sleep(); writing(push(1); self)}subopt2\')}")}\')}'
output: list[Instruction] = parse_variables(fact4)
for i in output:
    print(i)

executor: DebugInstructionExecutor = DebugInstructionExecutor(BotClient(None, None), pure_output=False)
asyncio.run(
    executor.run(output, interaction=None)
)
print(executor.output)