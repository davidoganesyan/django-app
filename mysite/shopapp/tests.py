from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices

from django.conf import settings
from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCAse(TestCase):
    def setUp(self):
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(reverse("shopapp:product_create"),
                                    {"name": self.product_name, "price": "100", "description": "Some product",
                                     "discount": "10"})
        print(response)
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = ['product-fixtures.json', ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        # product = Product.objects.filter(archived=False).all()
        # product_ = response.context["products"]
        # for p, p_ in zip(product, product_):
        #     self.assertEqual(p.pk, p_.pk)
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrderListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bob_test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        # self.assertRedirects(response, str(settings.LOGIN_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'product-fixtures.json',
    ]

    def test_get_product_view(self):
        response = self.client.get(reverse("shopapp:products_export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bob", password="qwerty")
        cls.user.user_permissions.add(Permission.objects.get(codename="view_order"))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def tearDown(self):
        self.order.delete()

    def setUp(self):
        self.client.force_login(user=self.user)
        self.order = Order.objects.create(delivery_address="test_street", promocode="test_code", user=self.user)

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "street")
        self.assertContains(response, "code")
        self.assertEqual(response.context.get('user').username, "bob")
        self.assertEqual(response.context.get("object_list")[0].pk, 1)


class OrderExportViewTestCase(TestCase):
    fixtures = [
        "order-fixtures.json", "product-fixtures.json", "user-fixtures.json", "group-fixtures.json"
    ]

    @classmethod
    def setUpClass(cls):
        super(OrderExportViewTestCase, cls).setUpClass()
        cls.user = User.objects.create_user(username="bob", password="qwerty", is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_order_view(self):
        response = self.client.get(reverse("shopapp:orders_export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.id,
                "product": [
                    [product.id, product.name]
                    for product in order.products.all()],
            }
            for order in orders
        ]
        order_data = response.json()
        print(expected_data)
        print(expected_data)
        self.assertEqual(order_data['orders'], expected_data)
