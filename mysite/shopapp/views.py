"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
from csv import DictWriter
from timeit import default_timer
import logging

from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Product, Order, ProductImage
from .common import save_csv_products

from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from .forms import ProductForm, GroupForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils.decorators import method_decorator
from django.core.cache import cache

log = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter, DjangoFilterBackend, OrderingFilter,
    ]
    search_fields = ["name", "description"]

    filterset_fields = [
        "name", "description", "price", "discount", "archived",
    ]

    ordering_fields = [
        "name", "price", "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("hello products list")
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class LatestProductFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes and additions products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects.order_by("-created_at")[:3]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:100]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend, OrderingFilter,
    ]

    filterset_fields = [
        "delivery_address", "promocode", "created_at", "user", "products",
    ]

    ordering_fields = [
        "user", "delivery_address",
    ]


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('smartphone', 999),
            ('laptop', 1999),
            ('desktop', 2999),
        ]

        context = {
            'time_running': default_timer(),
            'products': products,
            'links': ["groups/", "products/", "orders/"],
            'items': 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")

        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsListVIew(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    def test_func(self):
        return self.request.user.is_staff

    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response


class ProductDetailView(DetailView):
    template_name = "shopapp/products-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductUpdateView(UserPassesTestMixin, UpdateView):

    def test_func(self):
        if self.request.user.username == str(self.get_object().created_by) or self.request.user.is_superuser:
            return True

    model = Product
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object, image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related('products')
    )


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/users_order_list.html"
    context_object_name = "orders"

    def get_queryset(self, **kwargs):
        owner = get_object_or_404(User, pk=self.kwargs["user_id"])
        print(owner)
        orders = Order.objects.select_related("user").filter(user=owner).prefetch_related('products')
        contex = {"USER": owner, "orders": orders, }
        return contex


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.select_related("user").prefetch_related('products')
    )


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


# class OrderExportView(UserPassesTestMixin, View):
#     def test_func(self):
#         if self.request.user.is_staff:
#             return True
#
#     def get(self, request: HttpRequest) -> JsonResponse:
#         orders = Order.objects.order_by("pk").all()
#         order_data = [
#             {
#                 "pk": order.pk,
#                 "delivery_address": order.delivery_address,
#                 "promocode": order.promocode,
#                 "user": order.user.id,
#                 "product": [
#                     [product.id, product.name]
#                     for product in order.products.all()],
#             }
#             for order in orders
#         ]
#         return JsonResponse({"orders": order_data})

class UserOrdersListExportView(View):
    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:
        cache_key = f"orders_data_export_for_user_{user_id}"

        orders_data = cache.get(cache_key)
        if orders_data is None:
            owner: User = get_object_or_404(User, pk=user_id)
            orders = (
                Order.objects
                .select_related("user")
                .prefetch_related("products")
                .order_by('pk')
                .filter(user=owner)
                .all()
            )
            orders_data = OrderSerializer(orders, many=True).data
            cache.set(cache_key, orders_data, timeout=120)
        return JsonResponse({"products": orders_data})
