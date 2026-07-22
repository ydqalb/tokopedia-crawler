import json
import aiofiles
from typing import Optional


class JsonFileSink:
    def __init__(self, file_path: str, log=None):
        self.file_path = file_path
        self.log = log
        self.file = None
        self.first_record = True

    async def start(self):
        self.file = await aiofiles.open(self.file_path, 'w', encoding='utf-8')
        await self.file.write('[\n')
        if self.log:
            self.log.ok(f"JSON file sink created: {self.file_path}")

    async def send(self, data: dict):
        try:
            if not self.first_record:
                await self.file.write(',\n')
            
            json_line = json.dumps(data, ensure_ascii=False, indent=2)
            await self.file.write(f'  {json_line}')
            self.first_record = False
            
            if self.log:
                self.log.ok(f"JSON data written")
        except Exception as e:
            if self.log:
                self.log.error(f"JSON write error → {e}")

    async def close(self):
        if self.file:
            await self.file.write('\n]')
            await self.file.close()
            if self.log:
                self.log.ok(f"JSON file closed: {self.file_path}")
