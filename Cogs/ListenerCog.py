import discord
from discord.ext import commands
import random as _r

from Managers.ReplyManager import ReplyData
from Managers.ConstantsManager import ConstantsManager
from Managers.VariableParser import process_fact


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, constants_manager: ConstantsManager) -> None:
        self.bot = bot
        self.cm = constants_manager

    @commands.Cog.listener("on_ready")
    async def on_ready_gaming(self):
        await self.bot.change_presence(activity=discord.Game(name="you like a fiddle"), status=discord.Status.idle)
        print(f"Bot ready in {len(self.bot.guilds)} servers")

    @commands.Cog.listener("on_message")
    async def replies_content_listener(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        global_replies: list[ReplyData] = self.cm.reply_manager.get_aliases()

        active_replies: list[str] = []
        for entry in global_replies:
            entry: ReplyData

            for trigger in entry.triggers:
                if message.content.lower().__contains__(process_fact(trigger.lower(), self.cm.facts_manager, message, self.bot)):
                    potential_reply: str | None = process_fact(entry.get_reply(), self.cm.facts_manager, message, self.bot)
                    if potential_reply:
                        active_replies.append(potential_reply)
                    break

        if active_replies:
            await message.reply(content=_r.choice(active_replies), mention_author=False)

    @commands.Cog.listener("on_message")
    async def random_message_content_replies(self, message: discord.Message):
        if message.author.bot:
            return

        await self.letter_only_replies(message)
        await self.number_replies(message)
        await self.saying_replies(message)

    async def letter_only_replies(self, message: discord.Message):
        letterdict = {"a": "b", "b": "c", "c": "d",
                      "d": "e", "e": "f", "f": "g",
                      "g": "h", "h": "i", "i": "j",
                      "j": "k", "k": "l", "l": "m",
                      "m": "n", "n": "o", "o": "p",
                      "p": "q", "q": "r", "r": "s",
                      "s": "t", "t": "u", "u": "v",
                      "v": "w", "w": "x", "x": "y",
                      "y": "z", "z": "a"}

        if len(message.content) != 1:
            return

        if message.content.lower() not in letterdict.keys():
            return

        if message.content.isupper():
            letter = letterdict[message.content.lower()].upper()
        else:
            letter = letterdict[message.content]
        await message.reply(mention_author=False, content=letter)

    async def number_replies(self, message: discord.Message):
        message_content = message.content.split()
        if not message_content:
            return

        number = message_content[0]
        for character in number:
            try:
                int(character)
            except ValueError:
                if character not in [".", ",", "-"]:
                    return

        if number.count("-") > 1:
            return

        if number.replace(".", "").replace(",", "").replace("-", "") == "":
            return

        try:
            number = float(number)
        except ValueError:
            if "," in number and "." in number:
                last_comma_index = number.rindex(",")
                last_period_index = number.rindex(".")
                try:
                    if last_comma_index > last_period_index:
                        number = number.replace(".", "")
                        number = number.replace(",", ".")
                        number = float(number)
                    else:
                        number = float(number.replace(",", ""))
                except ValueError:
                    number = float(number.replace(".", "").replace(",", ""))
            elif "," in number and number.count(",") == 1:
                number = float(number.replace(",", "."))
            else:
                number = float(number.replace(",", "").replace(".", ""))
        finally:
            # Todo: should work when demical() is used instead of float
            """
            format_str = "{{0:.{}g}}".format(sys.float_info.max_10_exp + 1)
            number_str = format_str.format(number + 1)
            """

            number_str = str(number + 1)
            if number_str.endswith(".0"):
                number_str = number_str.removesuffix(".0")

            await message.reply(mention_author=False, content=number_str)

    async def saying_replies(self, message: discord.Message):
        if _r.randint(1, 300) != 1:
            return
        await message.reply(mention_author=False, content=process_fact(self.cm.sayings.get_line(None), self.cm.facts_manager, message, self.bot))
