from django.urls import path
from .import views
urlpatterns = [

    path('',views.cartitems,name="cart"),
    path('add_cart/<int:product_id>/', views.add_cart, name = 'add_cart'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('remove_cart/<int:product_id>', views.remove_cart, name = 'cart_remove'),
    path('add_address', views.add_address, name = 'add_address')
    

]