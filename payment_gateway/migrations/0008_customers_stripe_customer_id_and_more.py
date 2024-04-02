# Generated by Django 5.0.3 on 2024-03-29 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0007_cards_delete_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customers',
            name='stripe_payment_method_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
