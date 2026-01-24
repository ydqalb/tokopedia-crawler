import asyncio
import json
from aiokafka import AIOKafkaConsumer

from app.consumer.postgres import PostgresClient
from app.utils.config import load_config
from app.utils.logger import Logger


async def main():
    log = Logger()
    config = load_config(env="base")

    consumer = AIOKafkaConsumer(
        config["kafka"]["topic"],
        bootstrap_servers=config["kafka"]["bootstrap_servers"],
        value_deserializer=lambda v: json.loads(v.decode()),
        group_id="postgres-consumer-asyarie-debug",
        auto_offset_reset="earliest",
    )

    postgres = PostgresClient(config["postgres"])

    await consumer.start()
    await postgres.connect()

    log.ok("Kafka → Postgres consumer started")

    try:
        async for msg in consumer:  
            data = msg.value

            if not isinstance(data, dict):
                log.warn("Skip: message is not dict")
                continue

            product = data.get("data")
            if not product:
                log.warn("Skip: missing 'data'")
                continue

            if data.get("pic") != "asyarie":
                continue

            product_id = product.get("product_id")
            if not product_id or not str(product_id).isdigit():
                log.warn(f"Skip invalid product_id → {product_id}")
                continue

            if not product.get("product_name"):
                log.warn(f"Skip product {product_id}: missing name")
                continue

            try:
                await postgres.insert_product(data)
                await postgres.insert_statistic(data)
                log.ok(f"Inserted product {data['data']['product_id']} into Postgres")

            except Exception as e:
                log.error(f"Postgres insert error → {e}")

    finally:
        await consumer.stop()
        await postgres.close()
        log.warn("Kafka → Postgres consumer stopped")


if __name__ == "__main__":
    asyncio.run(main())
