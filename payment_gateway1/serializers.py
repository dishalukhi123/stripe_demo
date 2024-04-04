from rest_framework import serializers
from .models import Customers , Cards , Products

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for field in self.fields.values():
                field.required = False

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price']
