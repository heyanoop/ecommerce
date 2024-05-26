from django.db import models
from categories.models import category
from django.urls import reverse

class product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products')

    def __str__(self):
        return f"{self.product.product_name} Image"