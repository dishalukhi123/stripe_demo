# Generated by Django 5.0.3 on 2024-04-01 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0013_customers_stripe_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cards',
            name='card_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]