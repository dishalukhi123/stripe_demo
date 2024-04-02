# Generated by Django 5.0.3 on 2024-03-28 13:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateway', '0006_alter_card_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_name', models.CharField(max_length=100)),
                ('card_number', models.CharField(max_length=16, unique=True)),
                ('exp_year', models.PositiveSmallIntegerField()),
                ('exp_month', models.PositiveSmallIntegerField()),
                ('cvc', models.CharField(max_length=4)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment_gateway.customers')),
            ],
            options={
                'db_table': 'cards',
            },
        ),
        migrations.DeleteModel(
            name='Card',
        ),
    ]
