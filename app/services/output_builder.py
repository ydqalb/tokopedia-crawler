def build_output(product):
    return {
        "pic": "asyarie",
        "data": product.model_dump(
            mode="json",
            exclude={"shop_domain", "extra_payload"}
        )
    }
