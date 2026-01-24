import discord
from discord.ext import commands


class NumberAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener("on_message")
    async def number_autoreplies(self, message: discord.Message):
        if message.author.bot:
            return

        # todo: NEEDS A COMPLETE REWRITE, FLOATING POINT ISSUES MOST OF THE TIME.
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