import argparse
import asyncio
import os

from app.utils.logger import Logger
from app.services.product_service import ProductService
from app.services.sink_manager import SinkManager
from app.services.output_builder import build_output
from app.utils.config import load_config
from app.crawler.client import TokopediaClient
from app.crawler.engine import CrawlerEngine
from app.crawler.payload import SearchPayloadBuilder
from app.crawler.rate_limiter import RateLimiter
from app.parser.product import ProductParser
from app.parser.url_parser import ProductURLParser
from app.parser.pdp_main_fetcher import ProductDetailFetcher
from app.parser.pdp_second_fetcher import PDPSecondaryFetcher
from app.producer.kafka import KafkaProducerClient


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keyword",
        default=os.getenv("CRAWL_KEYWORD"),
        required=False
    )
    parser.add_argument(
        "--max-page",
        type=int,
        default=int(os.getenv("CRAWL_MAX_PAGE", 1))
    )

    args = parser.parse_args()
    
    if not args.keyword:
        raise ValueError("Keyword must be provided via --keyword or CRAWL_KEYWORD")

    return args


def init_clients(config_base, config_detail):
    """Initialize crawler, parsers, and fetchers."""
    client = TokopediaClient(config_base)
    payload_builder = SearchPayloadBuilder()
    rate_limiter = RateLimiter(1.5)
    crawler = CrawlerEngine(client, payload_builder, rate_limiter)

    product_parser = ProductParser()
    url_parser = ProductURLParser()
    headers = config_detail["tokopedia"]["headers"]
    graphql_url = config_detail["tokopedia"]["graphql_url"]
    pdp_main_fetcher = ProductDetailFetcher(headers, graphql_url)
    pdp_second_fetcher = PDPSecondaryFetcher(headers, graphql_url)

    return crawler, product_parser, url_parser, pdp_main_fetcher, pdp_second_fetcher


def init_sink(config_detail, log):
    kafka_client = KafkaProducerClient(config_detail["kafka"])
    sink = SinkManager(kafka=kafka_client, log=log)
    return sink


async def crawl_and_process(keyword, max_page, crawler, parser, url_parser,
                            pdp_main_fetcher, pdp_second_fetcher, sink, log):
    product_service = ProductService(url_parser, pdp_main_fetcher, pdp_second_fetcher)

    async for raw in crawler.crawl(keyword, max_page):
        products = parser.parse(raw)
        log.info(f"Parsed {len(products)} products")

        for product in products:
            processed = await product_service.process(product, log)
            if not processed:
                continue

            data = build_output(processed)
            await sink.send(data)

        log.info("Batch finished\n")


async def main():
    args = parse_args()
    log = Logger()
    log.info(f"Start crawling keyword='{args.keyword}' max_page={args.max_page}")

    config_base = load_config(env="base")
    config_detail = load_config(env="detail")

    # Initialize clients
    crawler, parser, url_parser, pdp_main_fetcher, pdp_second_fetcher = init_clients(config_base, config_detail)

    # Initialize sinks
    sink = init_sink(config_detail, log)
    await sink.start()

    # Crawl and process products
    await crawl_and_process(
        args.keyword,
        args.max_page,
        crawler,
        parser,
        url_parser,
        pdp_main_fetcher,
        pdp_second_fetcher,
        sink,
        log
    )

    await sink.close()


if __name__ == "__main__":
    asyncio.run(main())
