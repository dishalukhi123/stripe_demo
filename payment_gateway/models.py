from django.db import models

class Customers(models.Model):
    name = models.CharField(max_length = 50,unique=True)
    email = models.EmailField(max_length = 50,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customers'


