from accounts.models import account
from django.db import models

# Create your models here.
class SavedAddress(models.Model):
    user = models.ForeignKey(account, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    
    
class Order(models.Model):
    user = models.ForeignKey(account, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20)
    date = models.DateField()