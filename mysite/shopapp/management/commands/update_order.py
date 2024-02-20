from django.core.management import BaseCommand
from shopapp.models import Order, Product


class Command(BaseCommand):
    """Update order"""

    def handle(self, *args, **options):
        self.stdout.write("Update order")

        order = Order.objects.first()
        if not order:
            self.stdout.write("No order fund")
            return
        products = Product.objects.all()

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(self.style.SUCCESS(f"Successful added products {order.products.all()} to order {order}"))
