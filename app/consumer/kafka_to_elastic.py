import asyncio
import json
from aiokafka import AIOKafkaConsumer

from app.consumer.elastic import ElasticClient
from app.utils.config import load_config
from app.utils.logger import Logger


async def main():
    log = Logger()
    config = load_config(env="base")

    consumer = AIOKafkaConsumer(
        config["kafka"]["topic"],
        bootstrap_servers=config["kafka"]["bootstrap_servers"],
        value_deserializer=lambda v: json.loads(v.decode()),
        group_id="elastic-consumer-asyarie-debug",
        auto_offset_reset="earliest",
    )

    elastic = ElasticClient(config["elastic"])

    await consumer.start()
    await elastic.start()

    log.ok("Kafka → Elasticsearch consumer started")

    try:
        async for msg in consumer:
            event = msg.value

            # 1. validasi basic
            if not isinstance(event, dict):
                log.warn("Skip: message is not dict")
                continue

            # 2. filter PIC
            if event.get("pic") != "asyarie":
                continue

            data = event.get("data")
            if not data:
                log.warn("Skip: missing 'data'")
                continue

            product_id = data.get("product_id")
            if not product_id:
                log.warn("Skip: missing product_id")
                continue

            try:
                await elastic.send(event)
                log.ok(f"Indexed product {product_id} to Elasticsearch")

            except Exception as e:
                log.error(f"Elasticsearch index error → {e}")

    finally:
        await consumer.stop()
        await elastic.close()
        log.warn("Kafka → Elasticsearch consumer stopped")


if __name__ == "__main__":
    asyncio.run(main())
