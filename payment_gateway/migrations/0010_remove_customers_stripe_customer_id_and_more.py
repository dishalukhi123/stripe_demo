# Generated by Django 5.0.3 on 2024-03-29 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0009_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customers',
            name='stripe_customer_id',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='stripe_payment_method_id',
        ),
    ]