# Generated by Django 5.0.3 on 2024-05-13 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart_items',
            name='added_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]