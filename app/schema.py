from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field, validator

from .utils import (uuid1_time_to_datetime)

class ProductSchema(BaseModel):
    """
    Schema representing product details.
    """
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: Optional[str] = Field(..., description="Title of the product")


class ProductListSchema(BaseModel):
    """
    Schema representing product details.
    """
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: Optional[str] = Field(..., description="Title of the product")
    price_str: Optional[str] = Field(..., description="RAW price")
    
class ProductScrapeEventSchema(BaseModel):
    """
    Schema representing a product scraping event.
    """
    uuid: UUID = Field(..., description="Unique event identifier")
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: Optional[str] = Field(None, description="Title of the product")
    price_str: Optional[str] = Field(None, description="Price of the product as a string")


class ProductScrapeEventDetailSchema(BaseModel):
    uuid: UUID = Field(..., description="Unique event identifier") # This is just to use it in the validator
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: Optional[str] = Field(None, description="Title of the product")
    price_str: Optional[str] = Field(..., description="RAW price")
    created: Optional[Any] = None

    @validator('created', pre=True, always=True)
    def set_created_from_uuid1(cls, created, values):
        uuid_obj = values.get('uuid', None)
        if uuid_obj:
            uuid_time = uuid_obj.time
            return uuid1_time_to_datetime(uuid_time).isoformat()
        return created
