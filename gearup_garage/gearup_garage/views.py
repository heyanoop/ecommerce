from django.shortcuts import render
from store.models import product

def home(request):
    user = request.session.get('user_id')
    products = product.objects.all() 
    context = {
        'products' : products
    }
    return render(request, 'index.html', context)