from timeit import default_timer
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
    }

    return render(request, 'shopapp/shop-index.html', context=context)
