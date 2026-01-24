from aiokafka import AIOKafkaProducer
import json

class KafkaProducerClient:
    name = "Kafka"

    def __init__(self, config: dict):
        self.topic = config["topic"]
        self.producer = AIOKafkaProducer(
            bootstrap_servers=config["bootstrap_servers"],
            key_serializer=lambda k: str(k).encode(),
            value_serializer=lambda v: json.dumps(v, default=str).encode()
        )

    async def start(self):
        await self.producer.start()

    async def send(self, data: dict):
        try:
            product = data.get("data", {})
            key = product.get("product_id")

            await self.producer.send_and_wait(
                self.topic,
                value=data,
                key=key
            )
        except Exception as e:
            print(f"Kafka send error: {e}")

    async def close(self):
        await self.producer.stop()
