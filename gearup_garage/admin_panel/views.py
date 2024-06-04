from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from accounts.models import account
from store.models import product
from categories.models import category
from store.models import product, ProductImage
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.text import slugify
from orders.models import Order, OrderProduct
import os
from coupon.models import Coupon
from datetime import datetime
import pytz
from offer_management.models import category_offer, product_offer

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
    instance = get_object_or_404(product, id=product_id)
    category_instance = category.objects.all()
    images = ProductImage.objects.filter(product=instance)
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_list = request.POST.get('category_dropdown')
        stock = request.POST.get('stock')
        
        category_inst = get_object_or_404(category, id=category_list)

        # Update the instance with the new data
        instance.product_name = product_name
        instance.description = description
        instance.price = price
        instance.category = category_inst
        instance.stock = stock
        
        prod_images = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
        
        if all(prod_images) and len(prod_images) == 3:
            Prod_oldImages = ProductImage.objects.filter(product=instance)
            Prod_oldImages.delete()
            for image in prod_images:
                if image:
                    ProductImage.objects.create(product=instance, image=image)
            instance.save()
            messages.success(request, "Product updated successfully")
        else:
            messages.error(request, "3 images required")
            return redirect("edit_product", product_id=instance.id)
        return redirect('edit_product', product_id=instance.id)

    context = {
        'instance': instance,
        'category_instance': category_instance,
        'images': images,
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
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        category_id = request.POST.get('category_dropdown')
        category_inst = get_object_or_404(category, id=category_id)
        slug = slugify(product_name)

        # Create the product instance
        product_instance = product.objects.create(
            product_name=product_name,
            slug=slug,
            price=price,
            stock=stock,
            description=description,
            category=category_inst
        )

        # Handle multiple image uploads
        prod_images = [request.FILES.get('image1'), request.FILES.get('image2'), request.FILES.get('image3')]
        
        if all(prod_images) and len(prod_images) == 3:
            for image in prod_images:
                if image:
                    ProductImage.objects.create(product=product_instance, image=image)
            messages.success(request, "Product added successfully")
        else:
            product_instance.delete()  # Delete the product instance if not all images are provided
            messages.error(request, "3 images are required")
            return redirect('add_product')

        return redirect('add_product')

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

@login_required
@admin_required
def coupon_manager(request):
    coupons = Coupon.objects.all().order_by('-valid_until')
    context = {
        'coupons': coupons
    }
    return render(request, 'myadmin/home/coupon.html', context)

@login_required
@admin_required
def add_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        discount = request.POST.get('discount')
        date_from = request.POST.get('date_from')
        expiry_date = request.POST.get('expiry_date')

        if not code or not discount or not date_from or not expiry_date:
            messages.error(request, 'All fields are required.')
            return redirect('add_coupon')

        try:
            discount = int(discount)
            if discount < 1 or discount > 70:
                messages.error(request, 'Discount must be between 1 and 70.')
                return redirect('add_coupon')

            date_from = datetime.strptime(date_from, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

            if date_from >= expiry_date:
                messages.error(request, 'Expiry date must be after the start date.')
                return redirect('add_coupon')

        except ValueError:
            messages.error(request, 'Invalid data format.')
            return redirect('add_coupon')

        coupon = Coupon(code=code, discount=discount, valid_from=date_from, valid_until=expiry_date)
        coupon.save()
        messages.success(request, 'Coupon added successfully.')
        return redirect('add_coupon')

    return render(request, 'myadmin/home/add_coupon.html')

@login_required
def toggle_coupon_active(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'True'
        coupon.is_active = is_active
        coupon.save()
    return redirect('coupon')

@login_required
def sales_report(request):
    orders = Order.objects.filter(status = 'DELIVERED')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    context = {
        'order_details': orders,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'myadmin/home/sales_report.html', context)


def cat_offer(request):
    all_offers = category_offer.objects.all()
    context = {
        'all_offers': all_offers
    }
    return render(request, 'myadmin/home/offer_module_cat.html', context)

def prod_offer(request):
    all_offers = product_offer.objects.all()
    context = {
        'all_offers':all_offers
    }
    return render(request,  'myadmin/home/offer_module_prod.html', context)


def add_product_offer(request):
    product_list = product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product')
        valid_from = request.POST.get('date_from')
        valid_until = request.POST.get('expiry_date')
        discount = request.POST.get('discount')
        
        valid_from = datetime.strptime(valid_from, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        valid_until = datetime.strptime(valid_until, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

        try:
            selected_product = product.objects.get(id=product_id)
            
            # Check if the product is part of any active category offer
            active_category_offers = category_offer.objects.filter(
                category=selected_product.category,
                valid_from__lte=valid_until,
                valid_until__gte=valid_from
            )
            if active_category_offers.exists():
                messages.error(request, 'This product is part of an active category offer.')
                return redirect('add_product_offer')
            
            # Create product offer
            product_off = product_offer.objects.create(
                product=selected_product,
                valid_from=valid_from,
                valid_until=valid_until,
                discount=discount
            )
            product_off.save()

            # Update product price and old price
            selected_product.old_price = selected_product.price
            selected_product.price = selected_product.price - (selected_product.price * (int(discount) / 100))
            selected_product.save()

            messages.success(request, 'Product offer added successfully and product price updated.')
            return redirect('add_product_offer')
        except Exception as e:
            messages.error(request, 'Error adding product offer: ' + str(e))

    context = {
        'product_list': product_list
    }
    
    return render(request, 'myadmin/home/add_product_offer.html', context)

def add_category_offer(request):
    category_list = category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        discount = request.POST.get('discount')
        valid_from = request.POST.get('date_from')
        valid_until = request.POST.get('expiry_date')
        
        valid_from = datetime.strptime(valid_from, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        valid_until = datetime.strptime(valid_until, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

        try:
            selected_category = category.objects.get(id=category_id)
            
            # Check if any product in this category has an active product offer
            active_product_offers = product_offer.objects.filter(
                product__category=selected_category,
                valid_from__lte=valid_until,
                valid_until__gte=valid_from
            )
            if active_product_offers.exists():
                messages.error(request, 'There are active product offers in this category.')
                return redirect('add_category_offer')
            
            # Create category offer
            category_off = category_offer.objects.create(
                category=selected_category,
                discount=discount,
                valid_from=valid_from,
                valid_until=valid_until
            )
            category_off.save()

            # Update price for all products in the category
            products_in_category = product.objects.filter(category=selected_category)
            for prod in products_in_category:
                prod.old_price = prod.price
                prod.price = prod.price - (prod.price * (int(discount) / 100))
                prod.save()

            messages.success(request, 'Category offer added successfully and product prices updated.')
            return redirect('add_category_offer')
        except Exception as e:
            messages.error(request, 'Error adding category offer: ' + str(e))

    context = {
        'category_list': category_list
    }
    return render(request, 'myadmin/home/add_category_offer.html', context)


def delete_category_offer(request, offer_id):
    try:
        category_off = get_object_or_404(category_offer, id=offer_id)

        products_in_category = product.objects.filter(category=category_off.category)
        for prod in products_in_category:
            if prod.old_price:
                prod.price = prod.old_price
                prod.old_price = 0
                prod.save()

        category_off.delete()

        messages.success(request, 'Category offer deleted successfully and product prices updated.')
    except Exception as e:
        messages.error(request, 'Error deleting category offer: ' + str(e))

    return redirect('category_offer')

def delete_product_offer(request, offer_id):
    try:
        product_off = get_object_or_404(product_offer, id=offer_id)

        if product_off.product.old_price:
            product_off.product.price = product_off.product.old_price
            product_off.product.old_price = 0
            product_off.product.save()

        product_off.delete()

        messages.success(request, 'Product offer deleted successfully and product price updated.')
    except Exception as e:
        messages.error(request, 'Error deleting product offer: ' + str(e))

    return redirect('product_offer')