from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Order


class Command(BaseCommand):
    """Create order"""

    def handle(self, *args, **options):
        self.stdout.write("Create order")
        user = User.objects.get(username="admin")
        order = Order.objects.get_or_create(
            delivery_address='ul Pushkina d 8',
            promocode='SALE123',
            user=user
        )
        self.stdout.write(f"Created order {order}")
        self.stdout.write(self.style.SUCCESS("Order created"))
