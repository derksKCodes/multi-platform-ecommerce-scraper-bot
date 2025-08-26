from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StockStatus(str, Enum):
    IN_STOCK = "In Stock"
    OUT_OF_STOCK = "Out of Stock"
    LIMITED_STOCK = "Limited Stock"
    PRE_ORDER = "Pre-Order"

class DeliveryOption(BaseModel):
    company: str
    type: str
    price: str
    eta: str
    conditions: Optional[str] = None

class CheckoutScenario(BaseModel):
    scenario_name: str
    delivery_options: List[DeliveryOption]
    screenshot_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ProductData(BaseModel):
    name: str
    price: str
    discount_price: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    product_url: str
    image_urls: List[str] = []
    stock_status: StockStatus
    rating: Optional[str] = None
    reviews: Optional[str] = None
    seller: Optional[str] = None
    shipping_info: Optional[str] = None

    @validator('image_urls', pre=True)
    def validate_image_urls(cls, v):
        if isinstance(v, str):
            return [v]
        return v

class ScrapedResult(BaseModel):
    store: str
    url: str
    product: ProductData
    scenarios: Dict[str, CheckoutScenario] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

    class Config:
        use_enum_values = True