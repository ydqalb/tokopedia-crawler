from app.schema.product import Product
from datetime import datetime

def format_datetime(dt_str):
    if not dt_str:
        return None
    try:
        parsed = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return dt_str

class ProductEnricher:

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
            return None
        
        pdp_main = data.get("pdpMainInfo")
        if not pdp_main:
            return None
        
        main_data = pdp_main.get("data")
        if not main_data:
            return None
        
        basic = main_data.get("basicInfo")
        if not basic:
            return None
        
        extraPayload = pdp_main.get("extraPayload")
        if extraPayload:
            product.extra_payload = extraPayload

        product.product_id = basic.get("productID")
        product.product_url = basic.get("url")
        product.product_date = format_datetime(basic.get("createdAt"))

        stats = basic.get("stats") or {}
        tx = basic.get("txStats") or {}

        product.rating = stats.get("rating")
        product.sell_count = tx.get("countSold")

        components = pdp_main.get("components") or []

        for comp in components:
            comp_type = comp.get("type")
            comp_data = comp.get("data") or []

            if comp_type == "product_content" and comp_data:
                campaign = comp_data[0].get("price") or {}
                product.discount = campaign.get("discPercentage") or None

            if comp_type == "product_detail" and comp_data:
                product.description = (
                    comp_data[0]
                    .get("productDetailDescription", {})
                    .get("content")
                )

        return product
