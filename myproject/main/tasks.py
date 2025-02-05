from celery import shared_task
from parsers.aliexpress_parser import parse_test_site, save_to_db

@shared_task
def parse_products_task():
    print("Starting automatic parser...")
    products = parse_test_site()
    if products:
        save_to_db(products)
    print("Parsing completed!") 