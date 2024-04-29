from django.shortcuts import render
from accounts.models import account

# Create your views here.
def dashboard(request, user):
    user_data = account.objects.get(id = user)
    context = {
        'user_data':user_data
    }
    return render(request,'user/dashboard.html', context)