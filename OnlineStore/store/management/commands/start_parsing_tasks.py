import decimal
import time

import requests
import schedule
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from store.models import Item, ItemTag, ParsedPricesForItem


def start_parsing_from_enter_kg():
    url = 'https://enter.kg/computers/noutbuki_bishkek'

    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')

    db_products = set(
        list(Item.objects.filter(
            tags__in=ItemTag.objects.filter(slug='tech')
        ).values_list('title', flat=True))
    )
    products = soup.find_all('div', class_='rows')

    for product in products:
        product_name = getattr(
            product.find_next('span', class_='prouct_name'),
            'text', None
        )
        price = getattr(product.find_next('span', class_='price'), 'text', None)

        if product_name and price and product_name in db_products:
            source_price = price.text.replace(' Сом', '')
            ParsedPricesForItem.objects.create(
                item_id=Item.objects.get(title=product_name).id,
                source="Enter.kg",
                price=decimal.Decimal(source_price),
            )


def start_parsing_systema_kg():
    url = 'https://systema.kg/search?controller=search&s='

    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')

    db_products = set(
        list(Item.objects.filter(
            tags__in=ItemTag.objects.filter(slug='tech')
        ).values_list('title', flat=True))
    )
    products = soup.find_all('div', class_='js-product product')

    for product in products:
        product_name = getattr(
            product.find_next('div', class_='product-title'),
            'text', None
        )
        product_name = getattr(
            product_name.find_next('a'),
            'text',
            None
        ) if product_name else None
        price = getattr(product.find_next('span', class_='price'),
                        'text', None)

        if product_name and price and product_name in db_products:
            source_price = price.text.replace(' COM', '')
            ParsedPricesForItem.objects.create(
                item_id=Item.objects.get(title=product_name).id,
                source="Systema.kg",
                price=decimal.Decimal(source_price),
            )


class Command(BaseCommand):
    def handle(self, *args, **options):
        schedule.every().day.do(start_parsing_from_enter_kg)
        schedule.every().day.do(start_parsing_systema_kg)

        while True:
            schedule.run_pending()
            time.sleep(1)
