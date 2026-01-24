class ProductValidator:
    REQUIRED_FIELDS = [
        "product_id",
        "product_name",
        "price",
        "product_url",
        "scraped_at",
    ]

    def validate(self, data: dict) -> bool:
        for field in self.REQUIRED_FIELDS:
            if data.get(field) in (None, ""):
                return False
        return True
