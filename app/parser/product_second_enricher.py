from app.schema.product import Product

class ProductSpecificationEnricher:

    @staticmethod
    def enrich(product: Product, pdp_raw) -> Product:
        if isinstance(pdp_raw, list):
            if not pdp_raw:
                return product
            pdp_entry = pdp_raw[0]
        else:
            pdp_entry = pdp_raw or {}

        data = pdp_entry.get("data")
        if not data:
            return product

        pdp_main = data.get("pdpMainInfo")
        if not pdp_main:
            return product

        main_data = pdp_main.get("data")
        if not main_data:
            return product

        product_detail = main_data.get("productDetail")
        if not product_detail:
            return product

        contents = product_detail.get("content") or []
        if not contents:
            return product

        if product.specifications is None:
            product.specifications = {}

        specs: dict = {}

        for item in contents:
            title = (item.get("title") or "").strip().lower()
            subtitle = item.get("subtitle")

            if not subtitle:
                continue

            if title == "kondisi":
                specs["condition"] = subtitle

            elif title == "berat satuan":
                specs["weight"] = subtitle

            elif title in ("min. beli", "minimum beli"):
                specs["minimum_purchase"] = subtitle

            elif title == "kondisi penyimpanan":
                specs["storage_condition"] = subtitle

            elif title == "kategori":
                specs["category"] = subtitle

            elif title == "etalase":
                specs["etalase"] = subtitle

        if specs:
            product.specifications.update(specs)

        return product
