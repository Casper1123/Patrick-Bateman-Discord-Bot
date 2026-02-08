import discord
from discord.ext import commands
import re
from urllib.parse import urlparse


async def embedify(bot: commands.Bot, message: discord.Message, reply: bool = True, message_jump_link: bool = True) -> list[discord.Embed]:
    embed = discord.Embed()
    embed.set_author(
        name=f"{message.author.name if message.author.name else message.author.global_name} in {message.channel.name}",
        icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)

    attachment: discord.Attachment = _has_media_attachment(message)
    embed.description = ""
    if _is_auto_embedded(message.content):
        embed.set_image(url=_extract_embedded_url(message.content))
    elif attachment is not None:
        embed.set_image(url=attachment.url)
        embed.description = message.content
    else:
        embed.description = message.content

    if message_jump_link:
        embed.description = embed.description + (f"\n\n[Jump to message]({message.jump_url})" if reply else "")

    # If this message is a reply, make an embed for that too.
    embeds: list[discord.Embed] = [embed]
    if message.type == discord.MessageType.reply and reply:
        # noinspection PyBroadException
        try:
            reply = await embedify(
                await bot.get_channel(message.channel.id).fetch_message(message.reference.message_id), reply=False, message_jump_link=False)
            embeds = [reply[0], embed]
        except:
            ...
    return embeds


def _is_auto_embedded(message: str):
    URL_REGEX = re.compile(r"^(https?://\S+)$")
    AUTO_EMBED_DOMAINS = {
        "tenor.com", "giphy.com", "media.discordapp.net", "cdn.discordapp.com"
    }
    IMAGE_VIDEO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".webm", ".mov"}

    markdown_link_regex = re.compile(r"\[.*?]\((https?://[^\s)]+)\)")
    match = markdown_link_regex.search(message)
    if match:
        message = match.group(1)

    if not URL_REGEX.match(message):
        return False  # Not a single-link message

    parsed_url = urlparse(message)
    domain = parsed_url.netloc
    path = parsed_url.path

    if domain in AUTO_EMBED_DOMAINS and any(path.endswith(ext) for ext in IMAGE_VIDEO_EXTENSIONS):
        return True  # Matches an auto-embed domain with a valid media file extension

    return False


def _has_media_attachment(message: discord.Message) -> discord.Attachment | None:
    for attachment in message.attachments:
        media_type = attachment.content_type.split("/")[0]
        if media_type in ["image"]:  # Videos unsupported. Unfortunately. If it ever changes, this is here. Not optimised for speed, of course. I wouldn't be doing this in Python if that were the case.
            return attachment
    return None


def _extract_embedded_url(message_content: str) -> str | None:
    markdown_link_regex = re.compile(r"\[.*?]\((https?://[^\s)]+)\)")  # Matches [text](link)
    url_regex = re.compile(r"^(https?://\S+)$")  # Matches standalone URLs
    file_extension_regex = re.compile(r"(\.png|\.jpg|\.jpeg|\.gif|\.webp|\.mp4|\.webm|\.mov)(\?.*)?$")

    # Check for Markdown-style link
    match = markdown_link_regex.search(message_content)
    if match:
        url = match.group(1)
    elif url_regex.match(message_content):
        url = message_content
    else:
        return None  # No valid link found

    # Strip query parameters after the file extension
    stripped_url = file_extension_regex.sub(r"\1", url)
    return stripped_url