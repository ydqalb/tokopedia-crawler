import aiohttp
import asyncio

class TokopediaPDPClient:
    def __init__(self, config: dict):
        self.url = config["tokopedia"]["graphql_url"]
        self.headers = config["tokopedia"]["headers"]
        self.semaphore = asyncio.Semaphore(5)  # batasi concurrency

    async def fetch(self, session: aiohttp.ClientSession, payload: dict) -> dict:
        async with self.semaphore:
            async with session.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                return await resp.json()
