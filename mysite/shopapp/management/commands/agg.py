from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum
from shopapp.models import Product, Order


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products")
        )
        for order in orders:
            print(
                f"Order # {order.id} "
                f"with {order.products_count} "
                f"products worth {order.total}"
            )
        # result = Product.objects.filter(
        #     name__contains="smartphone",
        # ).aggregate(
        #     Avg("price"),
        #     Min("price"),
        #     max_price=Max("price"),
        #     count_products=Count("price"),
        # )
        # print(result)

        self.stdout.write(self.style.SUCCESS("Done"))
