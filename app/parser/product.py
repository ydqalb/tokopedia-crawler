from datetime import datetime
from typing import List

from app.schema.product import Product
from app.parser.validator import ProductValidator


class ProductParser:
    def __init__(self):
        self.validator = ProductValidator()

    def _extract_sell_count(self, label_groups: list | None) -> str | None:
        for label in label_groups or []:
            if label.get("position") == "ri_product_credibility":
                return label.get("title")
        return None

    def parse(self, raw: dict) -> List[Product]:
        if not raw or raw.get("errors"):
            return []

        products = (
            raw.get("data", {})
               .get("searchProductV5", {})
               .get("data", {})
               .get("products", [])
        )

        results: List[Product] = []

        for item in products:
            data = {
                "product_id": item.get("id"),
                "product_name": item.get("name"),
                "price": item.get("price", {}).get("number"),
                "product_url": item.get("url"),
                "product_image_url": item.get("mediaURL", {}).get("image"),
                "rating": float(item["rating"]) if item.get("rating") else None,
                "sell_count": self._extract_sell_count(item.get("labelGroups")),
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if self.validator.validate(data):
                results.append(Product(**data))

        return results
