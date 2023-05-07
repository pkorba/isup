import aiohttp
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from urllib.parse import urlparse, ParseResult


class IsUpBot(Plugin):
    @command.new(name="isup", help="check if website is online")
    @command.argument("message", pass_raw=True)
    async def isup(self, evt: MessageEvent, message: str) -> None:
        url = await self.parse_url(message)
        if not url.hostname:
            await evt.reply("I'm sorry. Address you provided is not a valid.")
            return
        try:
            full_url = url._replace(path="", params="", query="", fragment="").geturl()
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(full_url) as response:
                    if response.status < 400:
                        await evt.respond(f"{url.hostname} is up.")
                    else:
                        await evt.respond(f"{url.hostname} appears to be down from here.")
        except aiohttp.ServerTimeoutError:
            await evt.respond(f"Connection to {url.hostname} timed out. "
                              f"The site might be operational but under heavy load.")
        except aiohttp.ClientError as e:
            self.log.error(f"Connection failed: {url.hostname}: {e}")
            await evt.reply("I'm sorry. I wasn't able to carry out your request because "
                            "I ran into a problem connecting to the specified address.")

    @staticmethod
    async def parse_url(message: str) -> ParseResult:
        if not message.lower().startswith("http://") and not message.lower().startswith("https://"):
            message = f"https://{message}"
        url = urlparse(message)
        return url
