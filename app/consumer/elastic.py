from elasticsearch import AsyncElasticsearch
from datetime import datetime

class ElasticClient:
    def __init__(self, config: dict):
        self.index = config["index"]
        self.client = AsyncElasticsearch(config["hosts"])

    async def start(self):
        if not await self.client.ping():
            raise RuntimeError("Elasticsearch cluster unreachable")

    async def send(self, event: dict):
        if "data" not in event:
            return

        product = event["data"]

        specifications = product.get("specifications") or {}

        doc = {
            "product_id": int(product["product_id"]),
            "product_name": product.get("product_name"),
            "price": float(product.get("price") or 0),
            "discount": product.get("discount") or None,
            "product_url": product.get("product_url"),
            "product_image_url": product.get("product_image_url"),
            "rating": float(product.get("rating") or 0),
            "sell_count": int(product.get("sell_count") or 0),
            "scraped_at": datetime.fromisoformat(product.get("scraped_at")) if product.get("scraped_at") else None,
            "product_date": datetime.fromisoformat(product.get("product_date")) if product.get("product_date") else None,
            "description": product.get("description"),
            "specifications": specifications
        }

        # Insert ke Elasticsearch, pakai product_id sebagai document id
        await self.client.index(
            index=self.index,
            document=doc,
            id=doc["product_id"]
        )

    async def close(self):
        await self.client.close()
