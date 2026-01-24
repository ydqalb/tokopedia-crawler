from app.parser.product_main_enricher import ProductEnricher
from app.parser.product_second_enricher import ProductSpecificationEnricher

class ProductService:

    def __init__(self, url_parser, pdp_main_fetcher, pdp_second_fetcher):
        self.url_parser = url_parser
        self.pdp_main_fetcher = pdp_main_fetcher
        self.pdp_second_fetcher = pdp_second_fetcher

    async def process(self, product, log):
        # URL
        self.url_parser.enrich(product)

        if not product.product_id or not product.shop_domain:
            log.warn("Skip PDP (missing product_id / shop_domain)")
            return None

        # PDP main
        try:
            pdp_raw = await self.pdp_main_fetcher.fetch(product)
            enriched = ProductEnricher.enrich(product, pdp_raw)
            if not enriched:
                log.info(
                    f"Skip product (PDP not found): {product.product_url}"
                )
                return
            log.ok(f"PDP fetched → {product.product_name}")
        except Exception as e:
            log.error(f"PDP failed → {e}")
            return None

        # PDP spec
        try:
            spec_raw = await self.pdp_second_fetcher.fetch(product)
            ProductSpecificationEnricher.enrich(product, spec_raw)
        except Exception as e:
            log.warn(f"PDP spec skipped → {e}")

        return product
