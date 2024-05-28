from django.urls import path
from .import views
urlpatterns = [

    path('handlerequest/',views.handlerequest,name="handlerequest"),
    path('razorpay_success/',views.razorpay_success,name="razorpay_success"),
    
   

]