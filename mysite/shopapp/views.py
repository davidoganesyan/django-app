from timeit import default_timer

from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Product, Order

from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from .forms import ProductForm, OrderForm, GroupForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin


class ShopIndexView(View):
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
        }

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
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["products"] = Product.objects.all()
    #     return context


class ProductCreateView(CreateView):
    # def test_func(self):
    #     return self.request.user.groups.filter(name="creation_group").exists()
    #     return self.request.user.is_superuser
    # permission_required = "shopapp.add_product"
    # model = Product
    # fields = "name", "price", "description", "discount"
    # success_url = reverse_lazy("shopapp:products_list")
    #
    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     response = super().form_valid(form)
    #     return response
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")


class ProductDetailView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"

    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     product = get_object_or_404(Product, pk=pk)
    #     context = {
    #         "product": product
    #     }
    #     return render(request, 'shopapp/products-details.html', context=context)


class ProductUpdateView(UserPassesTestMixin, UpdateView):

    def test_func(self):
        if self.request.user.username == str(self.get_object().created_by) or self.request.user.is_superuser:
            return True

    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


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

        return JsonResponse({"products": products_data})


class OrderExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        order_data = [
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
        return JsonResponse({"orders": order_data})

#
# class Order(models.Model):
#     delivery_address = models.TextField(null=False, blank=True)
#     promocode = models.CharField(max_length=20, null=False, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     products = models.ManyToManyField(Product, related_name="orders")

# def shop_index(request: HttpRequest):
#     products = [
#         ('smartphone', 999),
#         ('laptop', 1999),
#         ('desktop', 2999),
#     ]
#
#     context = {
#         'time_running': default_timer(),
#         'products': products,
#         'links': ["groups/", "products/", "orders/"],
#     }
#
#     return render(request, 'shopapp/shop-index.html', context=context)
#
#
# def groups_list(request: HttpRequest):
#     context = {
#         "groups": Group.objects.prefetch_related('permissions').all(),
#
#     }
#     return render(request, 'shopapp/groups-list.html', context=context)
#
#
# def products_list(request: HttpRequest):
#     context = {
#         "products": Product.objects.all(),
#     }
#     return render(request, 'shopapp/products-list.html', context=context)
#
#
# def orders_list(request: HttpRequest):
#     context = {
#         "orders": Order.objects.select_related("user").prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)
#
#
# def create_product(request: HttpRequest) -> HttpResponse:
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # name = form.cleaned_data["name"]
#             # price = form.cleaned_data["price"]
#             # Product.objects.create(**form.cleaned_data)
#             form.save()
#             url = reverse("shopapp:products_list")
#             return redirect(url)
#     else:
#         form = ProductForm()
#
#     context = {
#         "form": form
#     }
#
#     return render(request, 'shopapp/create-product.html', context=context)


# def create_order(request: HttpRequest) -> HttpResponse:
#     if request.method == "POST":
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             url = reverse("shopapp:orders_list")
#             return redirect(url)
#     else:
#         form = OrderForm()
#
#     context = {
#         "form": form
#     }
#
#     return render(request, 'shopapp/order_form.html', context=context)
