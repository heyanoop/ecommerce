from django.shortcuts import redirect, render
from django.contrib import messages
from cart.models import Cart, Cart_items
from .models import Order, OrderProduct, Payment
from cart.models import Address
from cart.views import _cart_id
from django.db.models import F
from django.contrib.auth.decorators import login_required

def non_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'error.html', {'message': 'You are not authorized to access this page.'})
    return wrapper

@login_required
@non_admin_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        selected_address = Address.objects.get(id=address_id)
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = Cart_items.objects.filter(cart=cart)  
        order_total = sum(item.product.price * item.quantity for item in cart_items)
        tax = order_total * 2 / 100
        
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.error(request, f"Sorry, {cart_item.product.product_name} is out of stock.")
                return redirect('cart')  # Redirect back to the cart page if there is insufficient stock


        # Create order
        order = Order.objects.create(
            user=request.user,
            first_name=selected_address.first_name,
            last_name=selected_address.last_name,
            phone=selected_address.phone,
            email=selected_address.email,
            address_line_1=selected_address.address_line_1,
            address_line_2=selected_address.address_line_2,
            pincode=selected_address.pincode,
            country=selected_address.country,
            state=selected_address.state,
            city=selected_address.city,
            ip=request.META.get('REMOTE_ADDR'),
            address_type=selected_address.address_type,
            order_total=order_total,
            tax=tax,
            is_ordered=True,
        )

        # Create payment
        payment = Payment.objects.create(
            user=request.user,
            payment_method=payment_method,
            amount_paid=order_total + tax,
            status='completed'
        )

        # Create order products and decrease product quantity
        for cart_item in cart_items:
            # Decrease product quantity
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

            OrderProduct.objects.create(
                order=order,
                user=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product.price,
                ordered=True
            )

        # Delete cart items after order is placed
        cart_items.delete()  

        return render(request,'store/order_placed.html')
    else:
        return render(request, 'error.html', {'message': 'Invalid request method'})