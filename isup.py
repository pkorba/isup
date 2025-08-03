import aiohttp
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from urllib.parse import urlparse, ParseResult


class IsUpBot(Plugin):
    @command.new(name="isup", help="Check if a website is online")
    @command.argument("url", pass_raw=True, required=True)
    async def isup(self, evt: MessageEvent, url: str) -> None:
        await evt.mark_read()
        url = url.strip()
        if not url:
            await evt.reply("> **Usage:** !isup <url>")
            return
        url = await self.parse_url(url)
        if not url.hostname:
            await evt.reply("> Incorrect URL.")
            return

        headers = {
            "Sec-GPC": "1",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en,en-US;q=0.5",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0"
        }
        try:
            full_url = url._replace(path="", params="", query="", fragment="").geturl()
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(full_url) as response:
                    if response.status < 400:
                        await evt.reply(f"> {url.hostname} is up.")
                    else:
                        await evt.reply(f"> {url.hostname} is up, but server returns an error.")
        except TimeoutError:
            await evt.reply(f"> {url.hostname} is down.")
        except aiohttp.ClientError as e:
            self.log.error(f"Connection failed: {url.hostname}: {e}")
            await evt.reply(f"> Failed to check status of {url.hostname}. Connection error.")

    async def parse_url(self, url: str) -> ParseResult:
        if not url.lower().startswith(("http://", "https://")):
            url = f"https://{url}"
        new_url = urlparse(url)
        return new_url
