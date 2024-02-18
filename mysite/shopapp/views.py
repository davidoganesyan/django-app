from timeit import default_timer
from .models import Product, Order

from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.shortcuts import render


def shop_index(request: HttpRequest):
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


def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),

    }
    return render(request, 'shopapp/groups-list.html', context=context)


def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)


def orders_list(request: HttpRequest):
    context = {
        "orders": Order.objects.select_related("user").prefetch_related('products').all(),
    }
    return render(request, 'shopapp/orders-list.html', context=context)
