from Managers.CogBot import CogBot
from Managers.ConstantsManager import ConstantsManager

cm: ConstantsManager = ConstantsManager()
bot: CogBot = CogBot(cm)

if __name__ == "__main__":
    bot.run(cm._bot_token)
