from django.shortcuts import redirect, render
from django.contrib import messages
from cart.models import Cart, Cart_items
from .models import Order, OrderProduct, Payment
from cart.models import Address
from cart.views import _cart_id
from django.db.models import F
from django.contrib.auth.decorators import login_required
from coupon.models import Coupon
import razorpay 


def non_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'error.html', {'message': 'You are not authorized to access this page.'})
    return wrapper


from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from django.utils.decorators import method_decorator

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        selected_address = Address.objects.get(id=address_id)
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = Cart_items.objects.filter(cart=cart)  
        #order_total = sum(item.product.price * item.quantity for item in cart_items)
        #tax = order_total * 2 / 100
        
        coupon_code = request.session.get('coupon_code')
        original_price = request.session.get('original_price')
        tax = original_price * 0.2
    
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            coupon_discount = request.session.get('coupon_discount')
            print(coupon, coupon_code, coupon_discount)
            final_price = original_price - coupon_discount + tax
        else:
            final_price = original_price + tax
            coupon_discount = None
            coupon = None
        
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
            payment_method = payment_method,
            order_total=final_price,
            original_price = original_price,
            discount_price = coupon_discount,
            tax=tax,
            is_ordered=True,
            coupon_used = coupon,
            
            
        )
        request.session['order_id'] = order.id

        # Create payment
        payment = Payment.objects.create(
            user=request.user,
            payment_method=payment_method,
            amount_paid=final_price,
            status='completed'
        )

        if payment_method == 'debit_card':
            order = Order.objects.get(id = order.id )
            if order.razorpay_order_id is None:
                order_currency = 'INR'
                print('before')
                notes = {'order-type':"basic order from the website"}
                receipt_maker = str(order.id)
                    
                razorpay_order = razorpay_client.order.create(dict(
                amount=order.order_total*100,
                currency=order_currency,
                notes=notes,
                receipt=receipt_maker,
                payment_capture='1'  # Ensure this line is inside the dictionary
                ))  
                print('after')
                print(razorpay_order['id'])
                order.razorpay_order_id = razorpay_order['id']
                print(order.razorpay_order_id, order.id)
                order.save()
            total_amount =order.order_total*100
            callback_url = 'http://'+str(get_current_site(request))+"/payment_gateway/handlerequest/"
            print(callback_url)
            
            
                
            context ={
                'order':order,
                'razorpay_order_id':order.razorpay_order_id,
                'order_id':order.id,
                'total_amount':total_amount,
                'total_price': total_amount,
                'razorpay_merchant_id':settings.RAZORPAY_KEY_ID,
                'callback_url':callback_url
            }
            return render(request, 'store/razorpay_gateway.html',context)
        
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