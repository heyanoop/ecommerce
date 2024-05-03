from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import account
from cart.models import Address
from orders.models import OrderProduct, Order
from store.models import product

def regular_user_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')  # Or any other redirect you prefer
    return _wrapped_view_func

@login_required
@regular_user_required
def dashboard(request):
    user = {
        'user': request.user
    }
    return render(request, 'user/dashboard.html', user)

@login_required
@regular_user_required
def address_management(request):
    addresses = Address.objects.all()
    context = {
        'addresses': addresses
    }
    return render(request, 'user/address_management.html', context)

@login_required
@regular_user_required
def order_management(request):
    orders = OrderProduct.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'all_orders': orders
    }
    return render(request, 'user/myorder.html', context)

@login_required
@regular_user_required
def cancel_order(request, id):
    order = get_object_or_404(OrderProduct, id=id)
    if order.user != request.user:
        return redirect('home')
    
    order.ordered = False
    order.save()
    
    product = order.product  
    product.stock += order.quantity
    product.save()

    messages.success(request, 'Your order has been canceled.')
    return redirect('myorders')

@login_required
@regular_user_required
def edit_address(request, id):
    address = get_object_or_404(Address, pk=id)
    
    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        # Update address fields based on form data
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.pincode = request.POST.get('pincode')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.address_type = request.POST.get('address_type')
        
        # Save the updated address
        address.save()
        
        return redirect('manage_address')
    
    return render(request, 'user/edit_address.html', {'address': address})

def delete_address(request, id):
    address = get_object_or_404(Address, pk=id)
    address.delete()
    return redirect('manage_address')