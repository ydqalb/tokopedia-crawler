import asyncio

class CrawlerEngine:
    def __init__(self, client, payload_builder, rate_limiter):
        self.client = client
        self.payload_builder = payload_builder
        self.rate_limiter = rate_limiter

    async def crawl(self, keyword: str, max_page: int = 1):
        for page in range(1, max_page + 1):
            payload = self.payload_builder.build(keyword, page)

            raw = await self.client.post(payload)

            yield raw

            await self.rate_limiter.wait()
