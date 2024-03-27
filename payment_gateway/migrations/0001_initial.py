# Generated by Django 5.0.3 on 2024-03-26 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('card_number', models.CharField(max_length=16)),
                ('cvv', models.CharField(max_length=4)),
                ('expiry_date', models.CharField(max_length=5)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
