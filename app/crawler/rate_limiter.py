import asyncio
import time

class RateLimiter:
    def __init__(self, interval: float):
        self.interval = interval
        self._last_call = 0.0

    async def wait(self):
        elapsed = time.monotonic() - self._last_call
        sleep_time = self.interval - elapsed

        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

        self._last_call = time.monotonic()
