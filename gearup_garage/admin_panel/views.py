from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import account
from store.models import product
from categories.models import category
from store.models import product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.text import slugify



# Create your views here.
@login_required
@never_cache
def admin_login(request):
    return render(request, 'myadmin/accounts/login.html')

@login_required
@never_cache
def admin_dashboard(request):
    return render(request, 'myadmin/home/index.html')

@login_required
@never_cache
def user_list(request):
    user_data = account.objects.all()
    context = {
        'user': user_data
    }
    return render(request, 'myadmin/home/users.html', context)


@login_required
@never_cache
def product_list(request):
    product_data = product.objects.all()
    context = {
        'product' : product_data
    }
    return render(request, 'myadmin/home/product.html', context)

@login_required
def category_list(request):
    category_data = category.objects.all()
    context = {
        'category' : category_data
    }
    return render(request, 'myadmin/home/category.html', context)

@login_required
@never_cache
def user_edit(request, user_id):
    if not request.user.is_admin:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('user_list')
    
    instance = account.objects.get(id=user_id)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        is_admin = request.POST.get('is_admin')
        is_staff = request.POST.get('is_staff')
        is_active = request.POST.get('is_active')
        is_superadmin = request.POST.get('is_superadmin')
        
        instance.first_name = first_name
        instance.last_name = last_name
        instance.username = username
        instance.email = email
        instance.phone_number = phone_number
        instance.is_admin = True if is_admin == '1' else False
        instance.is_staff = True if is_staff == '1' else False
        instance.is_active = True if is_active == '1' else False
        instance.is_superadmin = True if is_superadmin == '1' else False
        instance.save()
        return redirect('user_list') 
    
    context = {
        'instance': instance,
    }
    return render(request, 'myadmin/home/edit_user.html', context)

@login_required
@never_cache
def edit_product(request, product_id):
    instance = product.objects.get(id=product_id)
    category_instance = category.objects.all()
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('images')
        category_list = request.POST.get('category_dropdown')
        stock = request.POST.get('stock')

        # Update the instance with the new data
        instance.product_name = product_name
        instance.description = description
        instance.price = price
        instance.category.category_name = category_list
        instance.stock  = stock
        if image:
            instance.images = image
        
        instance.save()
        
        return redirect('product_list')

    context = {
        'instance': instance,
        'category_instance' : category_instance,
    }
    return render(request, 'myadmin/home/edit_product.html', context)

@login_required
@never_cache
def edit_category(request, category_id):
    if not request.user.is_superadmin:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('category_list')
    
    category_instance = category.objects.get(id=category_id)
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        
        category_instance.description = description
        category_instance.category_name = category_name
        category_instance.save()
        return redirect ('category_list') 
    
    context  ={
        'category' : category_instance
        } 
    
    return render(request, 'myadmin/home/edit_category.html', context)

def add_product(request):
    category_instance = category.objects.all()
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        category_id = request.POST.get('category_dropdown')
        stock = request.POST.get('stock')

        # Generate slug
        slug = slugify(product_name)

        # Create a new instance
        new_product = product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            slug=slug,
            category_id=category_id
        )

        if image:
            new_product.images = image
            new_product.save()

        return redirect('product_list')

    context = {
        'category_instance': category_instance,
    }
    return render(request, 'myadmin/home/add_product.html', context)


def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        # Create a new category instance
        new_category = category.objects.create(
            category_name=category_name,
            description=description
        )

        return redirect('category_list')

    return render(request, 'myadmin/home/add_category.html')

def delete_category(request, category_id):
    category_instance = get_object_or_404(category, id=category_id)
    if request.method == 'POST':
        category_instance.delete()
        return redirect('category_list')

    context = {
        'category_instance': category_instance,
    }
    return render(request, 'myadmin/home/delete_category.html', context)