import decimal
import time

import requests
import schedule
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from django.db import IntegrityError

from store.models import Item, ItemTag, ParsedPricesForItem


def start_parsing_from_enter_kg():
    url = 'https://enter.kg/computers/noutbuki_bishkek'

    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')

    db_products = set(
        list(Item.objects.filter(
            tags__in=[ItemTag.objects.get(slug='laptops')]
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
            source_price = price.replace(' Сом', '')
            try:
                ParsedPricesForItem.objects.create(
                    item_id=Item.objects.get(title=product_name).id,
                    source="Enter.kg",
                    price=decimal.Decimal(source_price),
                )
            except IntegrityError:
                continue


def start_parsing_systema_kg():
    db_products = set(
        list(Item.objects.filter(
            tags__in=[ItemTag.objects.get(slug='laptops')]
        ).values_list('title', flat=True))
    )

    for product in db_products:
        url = f'https://systema.kg/search?controller=search&s={product}'
        print(url)
        content = requests.get(url).text
        soup = BeautifulSoup(content, 'html.parser')

        try:
            parsed_product = soup.find_all('div', class_='product')[0]
            print(parsed_product)
            product_name = parsed_product.find_next('h2', class_='product-title')
            product_name = getattr(
                product_name.find_next('a'),
                'text',
                None
            ) if product_name else None
            price = getattr(parsed_product.find_next('span', class_='price'),
                            'text', '')
            if product_name and price and product_name:
                print("ТОвары совпали")
                source_price = price.strip().replace(" СОМ", "").encode('unicode_escape').decode('utf-8')
                ParsedPricesForItem.objects.create(
                    item_id=Item.objects.get(title=product).id,
                    source="Systema.kg",
                    price=int(source_price),
                )
        except IndexError:
            print("INDEX ERROR")
            pass


class Command(BaseCommand):
    def handle(self, *args, **options):
        # start_parsing_from_enter_kg()
        start_parsing_systema_kg()
        # schedule.every().day.do(start_parsing_from_enter_kg)
        # schedule.every().day.do(start_parsing_systema_kg)
        #
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
