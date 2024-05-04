from django.shortcuts import render, get_object_or_404
from .models import product
from categories.models import category
from django.db.models import Q
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator

# Create your views here.
def store(request, category_slug = None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(category, slug = category_slug)
        products = product.objects.filter(category = categories, is_available  = True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
        
    else:
        
        products = product.objects.filter(is_available = True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products' : paged_product,
        'product_count' : product_count
    
    }
    return render(request, 'store/store.html', context)

def product_details(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug = category_slug, slug = product_slug)
        print(single_product)
        context = {
            'single_product' : single_product
        }
    except Exception as e:
        raise e
    
    return render(request, 'store/product_details.html', context)

def product_search(request):
   products = []
   product_count = 0
   if 'keyword' in request.GET:
       keyword = request.GET['keyword']
       if keyword:
           products = product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
           product_count = products.count()
   context = {
        'products':products,
        'product_count':product_count,
            }
           
   return render(request, 'store/store.html', context)