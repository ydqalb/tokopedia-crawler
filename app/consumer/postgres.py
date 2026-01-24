import asyncpg
from datetime import datetime
from typing import Optional

class PostgresClient:
    name = "Postgres"

    def __init__(self, config: dict, schema: str = "tokopedia_asyarie"):
        self.config = config
        self.conn: Optional[asyncpg.Connection] = None
        self.schema = schema
        self.pic = "asyarie"

    async def connect(self):
        self.conn = await asyncpg.connect(
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            host=self.config["host"],
            port=self.config.get("port", 5432),
        )
        await self._create_tables()

    async def _create_tables(self):
        await self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")

        # 🔹 dimension table
        await self.conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.schema}.raw_tokopedia_product_category_asyarie (
            category_id SERIAL PRIMARY KEY,
            category_name TEXT UNIQUE
        );
        """)

        # 🔹 product table
        await self.conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.schema}.raw_tokopedia_product_{self.pic} (
            product_id BIGINT PRIMARY KEY,
            product_name TEXT,
            price NUMERIC,
            discount TEXT,
            product_url TEXT,
            product_image_url TEXT,
            rating DOUBLE PRECISION,
            sell_count INTEGER,
            scraped_at TIMESTAMP,
            product_date TIMESTAMP,
            description TEXT,
            condition TEXT,
            weight TEXT,
            minimum_purchase TEXT,
            category_id INTEGER REFERENCES {self.schema}.raw_tokopedia_product_category_asyarie(category_id),
            etalase TEXT
        );
        """)

        # 🔹 statistic table
        await self.conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.schema}.raw_tokopedia_product_statistic_{self.pic} (
            id BIGSERIAL PRIMARY KEY,
            product_id BIGINT REFERENCES {self.schema}.raw_tokopedia_product_{self.pic}(product_id),
            crawling_date DATE,
            rating DOUBLE PRECISION,
            sell_count INTEGER,
            price NUMERIC,
            discount TEXT
        );
        """)

    # ======================
    # category helper
    # ======================
    async def _get_or_create_category(self, category_name: str | None) -> Optional[int]:
        if not category_name:
            return None

        await self.conn.execute(f"""
            INSERT INTO {self.schema}.raw_tokopedia_product_category_asyarie (category_name)
            VALUES ($1)
            ON CONFLICT (category_name) DO NOTHING
        """, category_name)

        row = await self.conn.fetchrow(f"""
            SELECT category_id
            FROM {self.schema}.raw_tokopedia_product_category_asyarie
            WHERE category_name = $1
        """, category_name)

        return row["category_id"] if row else None

    async def insert_product(self, data: dict):
        product = data["data"]

        sell_count = int(product.get("sell_count") or 0)
        price = float(product.get("price") or 0)
        discount = product.get("discount")
        rating = float(product.get("rating") or 0)

        scraped_at = (
            datetime.fromisoformat(product["scraped_at"])
            if product.get("scraped_at")
            else None
        )
        product_date = (
            datetime.fromisoformat(product["product_date"])
            if product.get("product_date")
            else None
        )

        specs = product.get("specifications") or {}
        condition = specs.get("condition")
        weight = specs.get("weight")
        minimum_purchase = specs.get("minimum_purchase")
        etalase = specs.get("etalase")

        # 🔹 category → id
        category_name = specs.get("category")
        category_id = await self._get_or_create_category(category_name)

        await self.conn.execute(f"""
            INSERT INTO {self.schema}.raw_tokopedia_product_{self.pic} (
                product_id, product_name, price, discount, product_url,
                product_image_url, rating, sell_count, scraped_at,
                product_date, description, condition, weight,
                minimum_purchase, category_id, etalase
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
            ON CONFLICT (product_id) DO NOTHING;
        """,
        int(product["product_id"]),
        product.get("product_name"),
        price,
        discount,
        product.get("product_url"),
        product.get("product_image_url"),
        rating,
        sell_count,
        scraped_at,
        product_date,
        product.get("description"),
        condition,
        weight,
        minimum_purchase,
        category_id,
        etalase
        )

    async def insert_statistic(self, data: dict):
        product = data["data"]

        await self.conn.execute(f"""
            INSERT INTO {self.schema}.raw_tokopedia_product_statistic_{self.pic} (
                product_id, crawling_date, rating, sell_count, price, discount
            )
            VALUES ($1,$2,$3,$4,$5,$6);
        """,
        int(product["product_id"]),
        datetime.now().date(),
        float(product.get("rating") or 0),
        int(product.get("sell_count") or 0),
        float(product.get("price") or 0),
        product.get("discount")
        )

    async def close(self):
        if self.conn:
            await self.conn.close()
