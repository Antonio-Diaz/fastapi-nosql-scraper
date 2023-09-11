import logging

from celery import Celery
from celery.schedules import crontab
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from celery.signals import beat_init, worker_process_init

from . import config, logger, db, models

settings = config.get_setting()
log_config = logger.LoggingConfig()
log_config.setup_logging()
logger = logging.getLogger(__name__)

Product = models.Product
ProductEventScrape = models.ProductScrapeEvent

celery_app = Celery(__name__)

celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url
celery_app.conf.broker_connection_retry_on_startup = True  # Add this line

def celery_on_startup(*args, **kwargs):
    try:
        logger.info("Initializing Cassandra connection for Celery.")
    
        if connection.cluster is not None:
            connection.cluster.shutdown()
        if connection.session is not None:
            connection.session.shutdown()
    
        cluster = db.CassandraSession.get_cluster()
        session = cluster.connect()
        default_connection = "default_connection"
        
        connection.register_connection(default_connection, session=session)
        connection.set_default_connection(default_connection)
    
        logger.info("Synchronizing Cassandra tables.")  # This should definitely print now
        sync_table(Product)
        sync_table(ProductEventScrape)
        logger.info("Cassandra initialization completed.")
    except Exception as e:
        logger.exception(f"An exception occurred: {e}")
        

beat_init.connect(celery_on_startup)
worker_process_init.connect(celery_on_startup)

# celery --app app.worker.celery_app worker --beat -s celerybeat-schedule --loglevel INFO
@celery_app.on_after_configure.connect
def setup_periodic_task(sender, *args, **kwargs):
    sender.add_periodic_task(crontab(minute="*/5"), scrape_products.s())

@celery_app.task
def list_product():
    q = Product.objects().all().values_list("asin", flat=True)
    print(list(q))

@celery_app.task
def scrape_asin(asin):
    logger.info(asin)

@celery_app.task
def scrape_products():
    logger.info("Doing scraping")
    q = Product.objects().all().value_list("asin", flat=True)
    for asin in q:
        scrape_asin.delay(asin)