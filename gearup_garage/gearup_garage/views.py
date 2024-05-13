from django.shortcuts import render
from store.models import product

def home(request):
    products = product.objects.filter(stock__gte=1).order_by('-views')[:8]
    context = {
        'products' : products
    }
    return render(request, 'index.html', context)