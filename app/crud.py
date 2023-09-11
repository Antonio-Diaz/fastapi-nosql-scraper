import copy
import uuid

from .db import CassandraSession
from .models import (Product, ProductScrapeEvent)


def create_entry(data: dict):
    """Creates a Product entry in the database."""
    # TODO: Add data validation here
    return Product.create(**data)

def create_scrape_event(data: dict):
    """Creates a ProductScrapeEvent entry in the database."""
    data['uuid'] = uuid.uuid1() 
    # TODO: Add data validation here
    return  ProductScrapeEvent.create(**data)

def add_scrape_event(data: dict, fresh=False):
    """Adds both a Product and a ProductScrapeEvent entry."""
    if fresh:
        data = copy.deepcopy(data)
    try:
        product = create_entry(data)
        scrape_obj = create_scrape_event(data)
    except Exception as e:  # Consider catching specific exceptions
        print(f"Failed to add scrape event: {e}")
        return None, None
    return product, scrape_obj
