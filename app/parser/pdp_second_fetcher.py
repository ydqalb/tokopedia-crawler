import httpx
from app.schema.product import Product


class PDPSecondaryFetcher:
    def __init__(self, headers: dict, graphql_url: str):
        self.headers = headers
        self.graphql_url = graphql_url

    def _build_payload(self, product: Product) -> list[dict]:
        return [
            {
                "operationName": "PDPSecondaryInfo",
                "variables": {
                    "productID": product.product_id,
                    "layoutID": "",
                    "extraPayload": product.extra_payload or "",
                    "queryParam": "",
                    "source": "P2",
                    "userLocation": {
                        "addressID": "33788809",
                        "districtID": "1663",
                        "postalCode": "40921",
                        "latlon": "-6.99,107.56",
                        "cityID": "148",
                    },
                },
                'query': 'query PDPSecondaryInfo($productID: String, $extraPayload: String, $source: String, $userLocation: pdpUserLocation) {\n  pdpMainInfo(productID: $productID, extraPayload: $extraPayload, source: $source, userLocation: $userLocation) {\n    data {\n      wishlistCount\n      shopFinishRate {\n        finishRate\n        __typename\n      }\n      shopInfo {\n        shopTier\n        badgeURL\n        closedInfo {\n          closedNote\n          reason\n          detail {\n            openDate\n            __typename\n          }\n          __typename\n        }\n        isOpen\n        favoriteData {\n          totalFavorite\n          alreadyFavorited\n          __typename\n        }\n        activeProduct\n        createInfo {\n          epochShopCreated\n          __typename\n        }\n        shopAssets {\n          avatar\n          __typename\n        }\n        shopCore {\n          domain\n          shopID\n          name\n          shopScore\n          url\n          ownerID\n          __typename\n        }\n        shopLastActive\n        location\n        statusInfo {\n          statusMessage\n          shopStatus\n          isIdle\n          __typename\n        }\n        isAllowManage\n        isOwner\n        ownerInfo {\n          id\n          __typename\n        }\n        isCOD\n        shopType\n        tickerData {\n          title\n          message\n          color\n          link\n          action\n          actionLink\n          tickerType\n          actionBottomSheet {\n            title\n            message\n            reason\n            buttonText\n            buttonLink\n            __typename\n          }\n          __typename\n        }\n        shopCredibility {\n          showOnlineStatus\n          showFollowButton\n          stats {\n            icon\n            value\n            __typename\n          }\n          __typename\n        }\n        partnerLabel\n        __typename\n      }\n      nearestWarehouses {\n        product_id\n        stock\n        stock_wording\n        price\n        warehouse_info {\n          warehouse_id\n          is_fulfillment\n          district_id\n          postal_code\n          geolocation\n          __typename\n        }\n        __typename\n      }\n      cartRedirection {\n        status\n        error_message\n        data {\n          product_id\n          config_name\n          hide_floating_button\n          available_buttons {\n            text\n            color\n            cart_type\n            onboarding_message\n            show_recommendation\n            __typename\n          }\n          unavailable_buttons\n          __typename\n        }\n        __typename\n      }\n      shopTopChatSpeed {\n        messageResponseTime\n        __typename\n      }\n      shopRatingsQuery {\n        ratingScore\n        __typename\n      }\n      shopPackSpeed {\n        hour\n        speedFmt\n        __typename\n      }\n      ratesEstimates {\n        warehouseID\n        products\n        data {\n          boBadge {\n            imageDesc\n            imageHeight\n            imageURL\n            isUsingPadding\n            __typename\n          }\n          destination\n          title\n          subtitle\n          chipsLabel\n          courierLabel\n          eTAText\n          cheapestShippingPrice\n          fulfillmentData {\n            icon\n            prefix\n            description\n            __typename\n          }\n          errors {\n            code: Code\n            message: Message\n            devMessage: DevMessage\n            __typename\n          }\n          shipmentBody {\n            icon\n            text\n            __typename\n          }\n          originalShippingRate\n          __typename\n        }\n        bottomsheet {\n          title\n          iconURL\n          subtitle\n          buttonCopy\n          __typename\n        }\n        __typename\n      }\n      restrictionInfo {\n        message\n        restrictionData {\n          productID\n          isEligible\n          action {\n            actionType\n            title\n            description\n            attributeName\n            badgeURL\n            buttonText\n            buttonLink\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      ticker {\n        tickerInfo {\n          productIDs\n          tickerData {\n            title\n            message\n            color\n            link\n            action\n            actionLink\n            tickerType\n            actionBottomSheet {\n              title\n              message\n              reason\n              buttonText\n              buttonLink\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      navBar {\n        name\n        items {\n          componentName\n          title\n          __typename\n        }\n        __typename\n      }\n      bebasOngkir {\n        products {\n          productID\n          boType\n          __typename\n        }\n        __typename\n      }\n      shipmentGrouping {\n        shipment {\n          componentName\n          componentType\n          detail {\n            shipmentv5 {\n              data {\n                productID\n                useBOVoucher\n                isCOD\n                metadata\n                warehouse_info {\n                  warehouse_id\n                  is_fulfillment\n                  district_id\n                  postal_code\n                  geolocation\n                  city_name\n                  ttsWarehouseID\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      productDetail {\n        content {\n          title\n          subtitle\n          applink\n          showAtFront\n          isAnnotation\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
            }
        ]

    async def fetch(self, product: Product) -> dict:
        payload = self._build_payload(product)

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.graphql_url,
                headers=self.headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
