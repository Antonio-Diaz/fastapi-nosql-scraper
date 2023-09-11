import logging

from typing import List
from fastapi import FastAPI, HTTPException
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.query import DoesNotExist
from . import (config, db, models, schema, logger, crud)

log_config = logger.LoggingConfig()
log_config.setup_logging()
logger = logging.getLogger(__name__)


settings = config.get_setting()
app = FastAPI()

session = None

def initialize_global_session():
    global session
    session = db.CassandraSession.get_session()
    if session is None:
        logger.error("Failed to initialize global DB session")
        raise Exception("Failed to initialize global DB session")

def initialize_database():
    sync_table(models.Product)
    sync_table(models.ProductScrapeEvent)

@app.on_event("startup")
async def on_startup():
    try:
        initialize_global_session()
        initialize_database()
        logger.info("Successfully initialized global session and database")
    except Exception as e:
        logger.error(f"Startup failed: {e}")


@app.get("/")
def read_index():
    global session
    if session:
        return {"Hello": "World", "name": settings.name}
    else:
        logger.error("Session not initialized")
        return {"Error": "Session not initialized"}

@app.get("/products", response_model=List[schema.ProductListSchema])
def products_list_view():
    try:
        products = list(models.Product.objects.all())
        if not products:
            logger.info("No products found")
            raise HTTPException(status_code=404, detail="No products found")
        return products
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/events/scrape")
def events_scrape_create_viwe(data: schema.ProductListSchema):
    try:
       product, _ = crud.add_scrape_event(data=dict(data))
       return product
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/products/{asin}")
def products_detail_view(asin: str):
    try:
        try:
            product = models.Product.objects.get(asin=asin)
        except DoesNotExist:
            logger.info(f"No product found with ASIN {asin}")
            raise HTTPException(status_code=404, detail="No product found")
        
        data = product._as_dict()  # Convierte el modelo Cassandra a un diccionario

        events = models.ProductScrapeEvent.objects(asin=asin)
        events_data = [schema.ProductScrapeEventDetailSchema(**event._as_dict()) for event in events]

        data['events'] = events_data
        data['events_url'] = f"/products/{asin}/events"
        return data

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/products/{asin}/events",
         response_model=List[schema.ProductScrapeEventDetailSchema])
def products_scrapes_list_view(asin: str):
    try:
        return list(models.ProductScrapeEvent.objects.filter(asin=asin))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
