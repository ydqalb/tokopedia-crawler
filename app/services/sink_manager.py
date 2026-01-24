class SinkManager:
    def __init__(self, kafka=None, postgres=None, elastic=None, log=None):
        self.kafka = kafka
        self.postgres = postgres
        self.elastic = elastic
        self.log = log

    async def start(self):
        if self.kafka:
            await self.kafka.start()
            self.log.ok("Kafka connected")

        if self.postgres:
            await self.postgres.connect()
            self.log.ok("Postgres connected")

        if self.elastic:
            await self.elastic.start()
            self.log.ok("Elastic connected")

    async def send(self, data):
        if self.kafka:
            try:
                await self.kafka.send(data)
                self.log.ok(f"Kafka sent to topic {self.kafka.topic}")
            except Exception as e:
                self.log.error(f"Kafka error → {e}")

        if self.postgres:
            try:
                await self.postgres.insert_product(data)
                await self.postgres.insert_statistic(data)
                self.log.ok("Postgres inserted raw + statistic")
            except Exception as e:
                self.log.error(f"Postgres error → {e}")

        if self.elastic:
            try:
                await self.elastic.send(data)
                self.log.ok(f"Elastic indexed {self.elastic.index}")
            except Exception as e:
                self.log.error(f"Elastic error → {e}")

    async def close(self):
        if self.kafka:
            await self.kafka.close()

        if self.postgres:
            await self.postgres.close()

        if self.elastic:
            await self.elastic.close()
