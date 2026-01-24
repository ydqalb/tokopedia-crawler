import httpx

class ProductDetailFetcher:
    def __init__(self, headers: dict, graphql_url: dict):
        self.headers = headers
        self.graphql_url = graphql_url

    def _build_payload(
        self,
        product_key: str,
        shop_domain: str,
        query_param: str = ""
    ) -> list[dict]:
        return [
            {
                "operationName": "PDPMainInfo",
                "variables": {
                    "productKey": product_key,
                    "shopDomain": shop_domain,
                    "layoutID": "",
                    "extraPayload": "",
                    "queryParam": query_param,
                    "source": "P1",
                    "userLocation": {
                        "addressID": "33788809",
                        "districtID": "1663",
                        "postalCode": "40921",
                        "latlon": "-6.99,107.56",
                        "cityID": "148",
                    },
                },
                'query': 'fragment ProductMedia on pdpDataProductMedia {\n  media {\n    type\n    urlOriginal: URLOriginal\n    urlThumbnail: URLThumbnail\n    urlMaxRes: URLMaxRes\n    videoUrl: videoURLAndroid\n    prefix\n    suffix\n    description\n    variantOptionID\n    __typename\n  }\n  videos {\n    source\n    url\n    __typename\n  }\n  __typename\n}\n\nfragment ProductHighlight on pdpDataProductContent {\n  name\n  price {\n    value\n    currency\n    priceFmt\n    slashPriceFmt\n    discPercentage\n    __typename\n  }\n  campaign {\n    campaignID\n    campaignType\n    campaignTypeName\n    campaignIdentifier\n    background\n    percentageAmount\n    originalPrice\n    discountedPrice\n    originalStock\n    stock\n    stockSoldPercentage\n    threshold\n    startDate\n    endDate\n    endDateUnix\n    appLinks\n    isAppsOnly\n    isActive\n    hideGimmick\n    showStockBar\n    __typename\n  }\n  thematicCampaign {\n    additionalInfo\n    background\n    campaignName\n    icon\n    __typename\n  }\n  stock {\n    useStock\n    value\n    stockWording\n    __typename\n  }\n  variant {\n    isVariant\n    parentID\n    __typename\n  }\n  wholesale {\n    minQty\n    price {\n      value\n      currency\n      __typename\n    }\n    __typename\n  }\n  isCashback {\n    percentage\n    __typename\n  }\n  isTradeIn\n  isOS\n  isPowerMerchant\n  isWishlist\n  isCOD\n  preorder {\n    duration\n    timeUnit\n    isActive\n    preorderInDays\n    __typename\n  }\n  __typename\n}\n\nfragment ProductInfo on pdpDataProductInfo {\n  row\n  content {\n    title\n    subtitle\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetail on pdpDataProductDetail {\n  title\n  productDetailDescription {\n    title\n    content\n    __typename\n  }\n  content {\n    title\n    subtitle\n    applink\n    showAtFront\n    isAnnotation\n    __typename\n  }\n  __typename\n}\n\nfragment ProductSocial on pdpDataSocialProof {\n  row\n  content {\n    icon\n    title\n    subtitle\n    applink\n    type\n    rating\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDataInfo on pdpDataInfo {\n  icon\n  title\n  isApplink\n  applink\n  content {\n    icon\n    text\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCustomInfo on pdpDataCustomInfo {\n  icon\n  title\n  isApplink\n  applink\n  separator\n  description\n  __typename\n}\n\nfragment ProductVariant on pdpDataProductVariant {\n  errorCode\n  parentID\n  defaultChild\n  sizeChart\n  totalStockFmt\n  variants {\n    productVariantID\n    variantID\n    name\n    identifier\n    option {\n      picture {\n        urlOriginal: url\n        urlThumbnail: url100\n        __typename\n      }\n      productVariantOptionID\n      variantUnitValueID\n      value\n      hex\n      stock\n      __typename\n    }\n    __typename\n  }\n  children {\n    productID\n    price\n    priceFmt\n    slashPriceFmt\n    discPercentage\n    optionID\n    optionName\n    productName\n    productURL\n    picture {\n      urlOriginal: url\n      urlThumbnail: url100\n      __typename\n    }\n    stock {\n      stock\n      isBuyable\n      stockWordingHTML\n      minimumOrder\n      maximumOrder\n      __typename\n    }\n    isCOD\n    isWishlist\n    campaignInfo {\n      campaignID\n      campaignType\n      campaignTypeName\n      campaignIdentifier\n      background\n      discountPercentage\n      originalPrice\n      discountPrice\n      stock\n      stockSoldPercentage\n      startDate\n      endDate\n      endDateUnix\n      appLinks\n      isAppsOnly\n      isActive\n      hideGimmick\n      isCheckImei\n      minOrder\n      showStockBar\n      __typename\n    }\n    thematicCampaign {\n      additionalInfo\n      background\n      campaignName\n      icon\n      __typename\n    }\n    ttsPID\n    ttsSKUID\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCategoryCarousel on pdpDataCategoryCarousel {\n  linkText\n  titleCarousel\n  applink\n  list {\n    categoryID\n    icon\n    title\n    isApplink\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetailMediaComponent on pdpDataProductDetailMediaComponent {\n  title\n  description\n  contentMedia {\n    url\n    ratio\n    type\n    __typename\n  }\n  show\n  ctaText\n  __typename\n}\n\nfragment PdpDataComponentShipmentV4 on pdpDataComponentShipmentV4 {\n  data {\n    productID\n    warehouse_info {\n      warehouse_id\n      is_fulfillment\n      district_id\n      postal_code\n      geolocation\n      city_name\n      ttsWarehouseID\n      __typename\n    }\n    useBOVoucher\n    isCOD\n    metadata\n    __typename\n  }\n  __typename\n}\n\nquery PDPMainInfo($productKey: String, $shopDomain: String, $layoutID: String, $extraPayload: String, $queryParam: String, $source: String, $userLocation: pdpUserLocation) {\n  pdpMainInfo(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, extraPayload: $extraPayload, queryParam: $queryParam, source: $source, userLocation: $userLocation) {\n    requestID\n    extraPayload\n    data {\n      layoutName\n      basicInfo {\n        alias\n        createdAt\n        isQA\n        id: productID\n        shopID\n        shopName\n        minOrder\n        maxOrder\n        weight\n        weightUnit\n        condition\n        status\n        url\n        needPrescription\n        catalogID\n        isLeasing\n        isBlacklisted\n        isTokoNow\n        defaultMediaURL\n        menu {\n          id\n          name\n          url\n          __typename\n        }\n        blacklistMessage {\n          imageURL\n          title\n          description\n          button\n          url\n          supportingImage {\n            url\n            width\n            height\n            __typename\n          }\n          __typename\n        }\n        category {\n          id\n          name\n          title\n          breadcrumbURL\n          isAdult\n          isKyc\n          minAge\n          detail {\n            id\n            name\n            breadcrumbURL\n            isAdult\n            __typename\n          }\n          ttsID\n          ttsDetail {\n            id\n            name\n            breadcrumbURL\n            isAdult\n            __typename\n          }\n          __typename\n        }\n        txStats {\n          transactionSuccess\n          transactionReject\n          countSold\n          paymentVerified\n          itemSoldFmt\n          __typename\n        }\n        stats {\n          countView\n          countReview\n          countTalk\n          rating\n          __typename\n        }\n        productID\n        ttsPID\n        ttsSKUID\n        ttsShopID\n        isAggregatedWithTTS\n        __typename\n      }\n      __typename\n    }\n    components {\n      name\n      type\n      kind\n      position\n      data {\n        ...ProductMedia\n        ...ProductHighlight\n        ...ProductInfo\n        ...ProductDetail\n        ...ProductSocial\n        ...ProductDataInfo\n        ...ProductCustomInfo\n        ...ProductVariant\n        ...ProductCategoryCarousel\n        ...ProductDetailMediaComponent\n        ...PdpDataComponentShipmentV4\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
            }
        ]

    async def fetch(self, product) -> dict:
        payload = self._build_payload(
            product_key=product.product_id,
            shop_domain=product.shop_domain,
        )

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.graphql_url,
                headers=self.headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
