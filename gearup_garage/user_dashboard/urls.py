from django.urls import path
from . import views

urlpatterns = [
    path('<int:user>/', views.dashboard, name = 'dashboard'),
]