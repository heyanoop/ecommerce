from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import account
from store.models import product
from categories.models import category
from store.models import product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.text import slugify
from orders.models import Order, OrderProduct

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

# Create your views here.
@login_required
@never_cache
def admin_login(request):
    return render(request, 'myadmin/accounts/login.html')

@login_required
@never_cache
@admin_required
def admin_dashboard(request):
    return render(request, 'myadmin/home/index.html')

@login_required
@never_cache
@admin_required
def user_list(request):
    user_data = account.objects.all()
    context = {
        'user': user_data
    }
    return render(request, 'myadmin/home/users.html', context)


@login_required
@never_cache
@admin_required
def product_list(request):
    product_data = product.objects.order_by('created_date').all()
    context = {
        'product' : product_data
    }
    return render(request, 'myadmin/home/product.html', context)

@login_required
@admin_required
def category_list(request):
    category_data = category.objects.order_by('category_name').all()
    context = {
        'category' : category_data
    }
    return render(request, 'myadmin/home/category.html', context)

@login_required
@never_cache
@admin_required
def user_edit(request, user_id):
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
        
        if account.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_user', user_id=user_id)
        
        if account.objects.filter(phone_number=phone_number).exclude(id=user_id).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('edit_user', user_id=user_id)
        
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
@admin_required
def edit_product(request, product_id):
    instance = product.objects.get(id=product_id)
    category_instance = category.objects.all()
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        category_list = request.POST.get('category_dropdown')
        stock = request.POST.get('stock')
        
        category_inst = category.objects.get(id=category_list)
        
        
        
        if product.objects.filter(product_name=product_name).exists():
            messages.error(request, "A product with this name already exists. Please choose a different name.")
        
        else:
        # Update the instance with the new data
            instance.product_name = product_name
            instance.description = description
            instance.price = price
            instance.category = category_inst
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
@admin_required
def edit_category(request, category_id):
    category_instance = category.objects.get(id=category_id)
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        
        category_instance.description = description
        category_instance.category_name = category_name
        category_instance.slug = slugify(category_name)
        category_instance.save()
        return redirect ('category_list') 
    
    context  ={
        'category' : category_instance
        } 
    
    return render(request, 'myadmin/home/edit_category.html', context)


@login_required
@admin_required
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

        if product.objects.filter(product_name=product_name).exists():
            messages.error(request, "A product with this name already exists. Please choose a different name.")
        else:
           
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

            messages.success(request, "Product added successfully.")
            return redirect('product_list')

    context = {
        'category_instance': category_instance,
    }
    return render(request, 'myadmin/home/add_product.html', context)



@login_required
@admin_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')

        # Check if a category with the same name already exists
        if category.objects.filter(category_name=category_name).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('add_category')

        # Create a new category instance
        new_category = category.objects.create(
            category_name=category_name,
            description=description,
            slug=slugify(category_name)
        )

        return redirect('category_list')

    return render(request, 'myadmin/home/add_category.html')

@login_required
@admin_required
def delete_category(request, category_id):
    category_instance = get_object_or_404(category, id=category_id)
    if request.method == 'POST':
        category_instance.delete()
        return redirect('category_list')

    context = {
        'category_instance': category_instance,
    }
    return render(request, 'myadmin/home/delete_category.html', context)

@login_required
@admin_required
def add_user(request):
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
        
        if account.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('add_user')
        
        if account.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('add_user')
        
        account.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            is_admin=True if is_admin == '1' else False,
            is_staff=True if is_staff == '1' else False,
            is_active=True if is_active == '1' else False,
            is_superadmin=True if is_superadmin == '1' else False
        )
        return redirect('user_list') 

    return render(request, 'myadmin/home/add_user.html')

@login_required
@admin_required
def delete_product(request, product_id):
    product_instance = get_object_or_404(product, id=product_id)
    if request.method == 'POST':
        product_instance.delete()
        return redirect('product_list')

    context = {
        'product_instance': product_instance,
    }
    return render(request, 'myadmin/home/delete_product.html', context)


def orders(request):
    all_orders = Order.objects.order_by('-created_at').all()
    context = {
        'all_orders':all_orders
    }
    return render(request,'myadmin/home/orders.html', context)


def delete_user(request, user_id):
    user_instance = get_object_or_404(account, id = user_id)
    user_instance.delete()
    context = {
        'user_instance': user_instance
    }
    return render(request, 'myadmin/home/delete_user.html', context)

def order_details(request, order_id):
    order_details = Order.objects.get(id=order_id)
    order_product = OrderProduct.objects.filter(order=order_details)
    print(order_product)
    context = {
        'order_details': order_details,
        'order_product': order_product,
        'final_price':order_details.order_total+order_details.tax
    }
    
    return render(request, 'myadmin/home/order_details.html', context)

@login_required
@admin_required
def update_order_status(request, status_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order = Order.objects.get(id=status_id)
        order_products = OrderProduct.objects.filter(order=order)
        order.status = new_status
        if order.status == 'CANCELLED':
            for order_product in order_products:
                product = order_product.product
                product.stock += order_product.quantity  # Increase stock by order quantity
                product.save() 
            
        order.save()
        return redirect('order_details', order_id=status_id)
