from django.urls import path
from .import views

urlpatterns = [
    path('', views.admin_login, name  = 'admin_login'),
    path('admin_dash/', views.admin_dashboard, name = 'admin_dash'),
    path('user_list/', views.user_list, name = 'user_list'),
    path('product_list/', views.product_list, name = 'product_list'),
    path('category_list/', views.category_list, name = 'category_list'),
    path('edit_user/<int:user_id>/', views.user_edit, name = 'edit_user'),
    path('edit_product/<int:product_id>/', views.edit_product, name = 'edit_product'),
    path('edit_category/<int:category_id>/', views.edit_category, name = 'edit_category'),
    path('add_product/', views.add_product, name = 'add_product'),
    path('add_category/', views.add_category, name = 'add_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('add_user/', views.add_user, name = 'add_user'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.orders, name = 'orders'),
    path('order_details/<int:order_id>/',views.order_details, name = 'order_details'),
    path('delete_user/<int:id>/', views.delete_user, name = 'delete_user'),
    path('update_status/<int:status_id>', views.update_order_status, name = 'update_order')
    
]