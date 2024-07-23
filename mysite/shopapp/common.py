from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    orders = []
    for row in reader:
        order = Order(
            delivery_address=row["delivery_address"],
            promocode=row["promocode"],
            user_id=row["user_id"]
        )
        order.save()
        for product in map(int, row["products"].split(',')):
            order.products.add(product)
        orders.append(order)

    return orders
