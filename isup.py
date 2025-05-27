import aiohttp
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from urllib.parse import urlparse, ParseResult


class IsUpBot(Plugin):
    @command.new(name="isup", help="check if website is online")
    @command.argument("message", pass_raw=True, required=True)
    async def isup(self, evt: MessageEvent, message: str) -> None:
        await evt.mark_read()
        message = message.strip()
        if not message:
            await evt.respond("Usage: !isup <url>")
            return
        url = await self.parse_url(message)
        if not url.hostname:
            await evt.reply("Incorrect URL.")
            return
        try:
            full_url = url._replace(path="", params="", query="", fragment="").geturl()
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(full_url) as response:
                    if response.status < 400:
                        await evt.reply(f"{url.hostname} is up.")
                    else:
                        await evt.reply(f"{url.hostname} is up, but server returns an error.")
        except TimeoutError:
            await evt.reply(f"{url.hostname} is down.")
        except aiohttp.ClientError as e:
            self.log.error(f"Connection failed: {url.hostname}: {e}")
            await evt.reply(f"Failed to check status of {url.hostname}. Connection error.")

    @staticmethod
    async def parse_url(message: str) -> ParseResult:
        if not message.lower().startswith("http://") and not message.lower().startswith("https://"):
            message = f"https://{message}"
        url = urlparse(message)
        return url
