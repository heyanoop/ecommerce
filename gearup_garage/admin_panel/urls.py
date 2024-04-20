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
]