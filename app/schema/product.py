from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    product_id: str
    product_name: str

    price: Optional[int] = None
    discount: Optional[str] = None

    product_url: Optional[str] = None
    product_image_url: Optional[str] = None
    rating: Optional[float] = None
    sell_count: Optional[str] = None
    scraped_at: str

    shop_domain: Optional[str] = None
    product_date: Optional[str] = None
    description: Optional[str] = None
    specifications: dict = Field(default_factory=dict)
    extra_payload: Optional[str] = None

    model_config = ConfigDict(extra="forbid")
