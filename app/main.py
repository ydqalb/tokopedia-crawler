import argparse
import asyncio
import os

from dotenv import load_dotenv
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
from app.consumer.json_file import JsonFileSink

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", action="append")
    parser.add_argument("--max-page", type=int, default=int(os.getenv("CRAWL_MAX_PAGE", 1)))
    parser.add_argument("--json-output", type=str, default=None, help="Path untuk output JSON file (default: output/{keyword}.json)")
    parser.add_argument("--enable-kafka", action="store_true", default=True, help="Enable Kafka output (default: True)")
    parser.add_argument("--skip-kafka", action="store_true", help="Skip Kafka output (disable Kafka)")

    args = parser.parse_args()

    keywords = args.keyword
    if not keywords:
        raw = os.getenv("CRAWL_KEYWORDS")
        if raw:
            keywords = [k.strip() for k in raw.split(",") if k.strip()]

    if not keywords:
        raise ValueError("Keyword must be provided via --keyword or CRAWL_KEYWORDS env")

    enable_kafka = not args.skip_kafka

    return keywords, args.max_page, args.json_output, enable_kafka


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


def init_sink(config_detail, log, json_output=None, enable_kafka=True):
    # Create output directory if json_output is specified
    if json_output:
        output_dir = os.path.dirname(json_output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            log.ok(f"Output directory created: {output_dir}")
    
    kafka_client = KafkaProducerClient(config_detail["kafka"]) if enable_kafka else None
    json_sink = JsonFileSink(json_output, log) if json_output else None
    sink = SinkManager(kafka=kafka_client, json_sink=json_sink, log=log)
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
    keywords, max_page, json_output_arg, enable_kafka = parse_args()
    log = Logger()

    # Ensure output directory exists
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        log.ok(f"Output directory created: {output_dir}")

    # Build json_output path - always default to output/ folder
    json_output = None
    if json_output_arg:
        # If user provided path, put it inside output/ folder (unless it's absolute path or already has output/)
        if not os.path.isabs(json_output_arg) and not json_output_arg.startswith("output/"):
            json_output = os.path.join(output_dir, json_output_arg)
        else:
            json_output = json_output_arg
    else:
        # If no path specified, auto-generate based on keywords
        if len(keywords) == 1:
            json_output = os.path.join(output_dir, f"{keywords[0]}.json")
        else:
            json_output = os.path.join(output_dir, "results.json")

    log.info(f"Start crawling keywords={keywords} max_page={max_page}")
    log.info(f"Kafka: {'enabled' if enable_kafka else 'disabled'} | JSON output: {json_output or 'disabled'}")

    config_base = load_config(env="base")
    config_detail = load_config(env="detail")

    crawler, parser, url_parser, pdp_main_fetcher, pdp_second_fetcher = init_clients(
        config_base, config_detail
    )

    sink = init_sink(config_detail, log, json_output, enable_kafka)
    await sink.start()

    for keyword in keywords:
        log.info(f"Start crawling keyword='{keyword}'")

        await crawl_and_process(
            keyword,
            max_page,
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
