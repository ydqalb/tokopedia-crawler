import re

TOKOPEDIA_PRODUCT_REGEX = re.compile(
    r"tokopedia\.com/([^/]+)/([^/?]+)"
)

class ProductURLParser:
    def enrich(self, product):
        if not product.product_url:
            return

        match = TOKOPEDIA_PRODUCT_REGEX.search(product.product_url)
        if not match:
            return

        product.shop_domain = match.group(1)
        product.product_id = match.group(2)  