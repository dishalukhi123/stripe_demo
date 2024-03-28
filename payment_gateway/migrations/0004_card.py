# Generated by Django 5.0.3 on 2024-03-28 04:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0003_alter_customers_name_alter_customers_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_name', models.CharField(max_length=100)),
                ('card_number', models.CharField(max_length=16)),
                ('exp_year', models.PositiveSmallIntegerField()),
                ('exp_month', models.PositiveSmallIntegerField()),
                ('cvc', models.CharField(max_length=4)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment_gateway.customers')),
            ],
            options={
                'db_table': 'card',
            },
        ),
    ]
