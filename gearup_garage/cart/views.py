from django.shortcuts import render, redirect
from .models import Cart, Cart_items, Address
from store.models import product
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product_instance = product.objects.get(id=product_id)
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        
    cart.save()
    
    try:
        cart_item = Cart_items.objects.get(cart=cart, product=product_instance)
        if cart_item.quantity < product_instance.stock:  # Check if there is enough stock to add to the cart
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Product added to cart")
        else:
            messages.warning(request, "No more stock available for this product")
    except Cart_items.DoesNotExist:
        if product_instance.stock > 0:  # Check if there is any stock available for the product
            cart_item = Cart_items.objects.create(product=product_instance, cart=cart, quantity=1)
            cart_item.save()
            messages.success(request, "Product added to cart")
        else:
            messages.warning(request, "No stock available for this product")
    
    return redirect('cart')


def cartitems(request):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    cart_items = Cart_items.objects.filter(cart = cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    tax = (total_price * 2/100)
    
    context = {
        'cart_items' : cart_items,
        'total_price': total_price,
        'tax': tax,
        'final_price': total_price+ tax
    }
    return render(request, 'store/cart.html', context)

def remove_cart(request, product_id):
    product_instance = product.objects.filter(id=product_id).first()  # Use .first() to get the first item or None
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = None  
    try:
        cart_item = Cart_items.objects.get(cart=cart, product=product_instance)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    except Cart_items.DoesNotExist:
        return redirect('cart')

@login_required
def checkout(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = Cart_items.objects.filter(cart=cart)
    user = request.user
    delivery_address = Address.objects.filter(user=user)
    context = {
        'cart_item': cart_items,
        'addresses': delivery_address
    }

    if cart_items.exists():
        return render(request, 'store/checkout.html', context)
    else:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')



def add_address(request):
    if request.method == 'POST':
        # Retrieve form data from POST request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        address_type = request.POST.get('address_type')

        # Create Address object
        address = Address.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            pincode=pincode,
            city=city,
            state=state,
            country=country,
            address_type=address_type
        )

        # Save the address
        address.save()
        
        # Redirect the user back to the checkout page
        return redirect('checkout')
