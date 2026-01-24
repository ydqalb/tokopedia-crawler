import requests
import asyncio

class TokopediaClient:
    def __init__(self, config):
        self.url = config["tokopedia"]["graphql_url"]
        self.headers = config["tokopedia"]["headers"]

    async def post(self, payload):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._sync_post,
            payload
        )

    def _sync_post(self, payload):
        resp = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        return resp.json()
