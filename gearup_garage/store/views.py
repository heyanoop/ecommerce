from django.shortcuts import render, get_object_or_404
from .models import product
from categories.models import category

# Create your views here.
def store(request, category_slug = None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(category, slug = category_slug)
        products = product.objects.filter(category = categories, is_available  = True)
        product_count = products.count()
        
    else:
        
        products = product.objects.filter(is_available = True)
        product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count
    
    }
    return render(request, 'store.html', context)