# Generated by Django 5.0.3 on 2024-04-01 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0012_customers_products_remove_paymenthistory_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='stripe_customer_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]