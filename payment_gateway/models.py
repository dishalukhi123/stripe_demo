from django.db import models

class Customers(models.Model):
    name = models.CharField(max_length = 50,unique=True)
    email = models.EmailField(max_length = 50,unique=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    stripe_customer_id = models.CharField(max_length=100, unique=True , null = True)   

    class Meta:
        db_table = 'customers'


class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products'

class Cards(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16 , unique=True)
    exp_year = models.PositiveSmallIntegerField()
    exp_month = models.PositiveSmallIntegerField()
    cvc = models.CharField(max_length=4)
    card_id = models.CharField(max_length=100 , null= True)


    class Meta:
        db_table = 'cards'

