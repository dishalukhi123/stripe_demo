from django.db import models

class Customers(models.Model):
    name = models.CharField(max_length = 50,unique=True)
    email = models.EmailField(max_length = 50,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customers'

class Card(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)
    exp_year = models.PositiveSmallIntegerField()
    exp_month = models.PositiveSmallIntegerField()
    cvc = models.CharField(max_length=4)


    class Meta:
        db_table = 'card'

