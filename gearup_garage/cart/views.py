from django.shortcuts import render, redirect
from .models import Cart, Cart_items
from store.models import product

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request,product_id):
    Product = product.objects.get(id = product_id)
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    try:
        cart_item = Cart_items.objects.get(cart = cart, product=Product)
        cart_item.quantity += 1
        cart_item.save()
    except Cart_items.DoesNotExist:
        cart_item = Cart_items.objects.create(product = Product, cart = cart, quantity = 1)
        cart_item.save()
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
    
    
    context = {
        'cart_item' : cart_items
    }
    return render(request, 'store/cart.html', context)