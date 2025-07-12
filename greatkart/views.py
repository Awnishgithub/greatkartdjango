from django.shortcuts import render
from store.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'product': products,
    }

    return render(request, 'home.html', context)

from django.shortcuts import render
from store.models import Product  # update path as needed

def home(request):
    products = Product.objects.all().filter(is_available=True)  # fetch top 8 products or popular ones
    return render(request, 'home.html', {'products': products})
