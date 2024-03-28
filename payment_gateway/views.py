from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import stripe
from rest_framework import generics
from .models import Customers , Card
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from django.core.exceptions import ValidationError
from django.db import IntegrityError


stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    session_id = "cs_test_a10c40aGAURYsEOvU4BDLOLhwqab92NF3RtQIm7dztOBn4mkfVoHty61J6"
    return render(request, 'index.html', {'session_id': session_id})


class Manage_Customer(APIView):
    def get(self, request):
        customers = Customers.objects.all()
        serialized_customers = []
        for customer in customers:
            serialized_customer = {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'created_at': customer.created_at
            }
            serialized_customers.append(serialized_customer)
        return Response({'customers': serialized_customers}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        try:
            if not data.get('email'):
                raise ValidationError('Email is required')
            if not data.get('name'):
                raise ValidationError('Name is required')
                
            customer = stripe.Customer.create(
                email=data.get('email'),
                name=data.get('name'),
            )

            try:
                customer_entry = Customers.objects.create(
                    name=data.get('name'),
                    email=data.get('email')
                )
            except IntegrityError:
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'customer': customer}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class Add_Card(APIView):
    def post(self, request):
        data = request.data
        try:
            if not data.get('customer_id'):
                raise ValidationError('Customer ID is required')
            if not data.get('card_token'):
                raise ValidationError('Card token is required')

            stripe.PaymentMethod.attach(
                data.get('card_token'),
                print('=-=-=-=-=-=-=-=-',data),
                customer=data.get('customer_id'),
            )

            return Response({'message': 'Card added successfully'}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
