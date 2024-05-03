from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('manage_address/', views.address_management, name = 'manage_address'),
    path('myorders/', views.order_management, name = 'myorders'),
    path('cancel/<int:id>', views.cancel_order, name = 'cancel_order'),
    path('edit_address/<int:id>/', views.edit_address, name = 'edit_address'),
    path('delete_address/<int:id>/', views.delete_address, name = 'delete_address')

]