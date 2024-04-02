from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import stripe
from rest_framework import generics
from .models import Customers , Cards , Products
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .serializers import CardSerializer, CustomersSerializer
from decimal import Decimal
from django.urls import reverse




stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    session_id = "cs_test_a1pMtJRsTGOg3t17dGDsjOONvmDWZ63PCFL7lYBCwo3pnFRWTl4cAk0Cba"
    return render(request, 'index.html', {'session_id': session_id})


class ManageCustomer(APIView):
    def get(self, request, customer_id=None):
        if customer_id:
            try:
                customer = Customers.objects.get(id=customer_id)
                serialized_customer = {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'created_at': customer.created_at,
                }
                return Response({'customer': serialized_customer}, status=status.HTTP_200_OK)
            except Customers.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            customers = Customers.objects.all()
            serialized_customers = []
            for customer in customers:
                serialized_customer = {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'created_at': customer.created_at,
                }
                serialized_customers.append(serialized_customer)
            return Response({'customers': serialized_customers}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        try:
            required_fields = ['email', 'name']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.capitalize()} is required')

            stripe.api_key = settings.STRIPE_SECRET_KEY

            customer = stripe.Customer.create(
                email=data.get('email'),
                name=data.get('name'),
            )

            customer_entry = Customers.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                stripe_customer_id=customer.id,
            )

            return Response({'customer_id': customer.id}, status=status.HTTP_201_CREATED)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def patch(self, request, customer_id):
        try:
            customer = Customers.objects.get(id=customer_id)
        except Customers.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            customer.email = data['email']

        customer.save()
        return Response({'message': 'Customer updated successfully'}, status=status.HTTP_200_OK)
        
        
    def delete(self, request, customer_id):
        try:
            customer = Customers.objects.get(id=customer_id)
        except Customers.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        

class CreatePaymentIntent(APIView):
    def post(self, request):
        data = request.data
        try:
            required_fields = ['customer_id', 'product_id', 'quantity', 'card_id']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.capitalize()} is required')

            product = Products.objects.get(id=data.get('product_id'))
            price = int(product.price) * int(data.get('quantity')) * 100

            stripe.api_key = settings.STRIPE_SECRET_KEY
            # return_url = 'https://example.com/payment/success'

            # Create a PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=price,
                currency='INR',
                customer=data.get('customer_id'),
                payment_method=data.get('card_id') ,
                # confirm=True, 
                metadata={'product_id': data.get('product_id'), 'quantity': data.get('quantity')},
            )
            # payment_intent.confirm()


            print('Payment Intent:', payment_intent)

            if payment_intent.payment_method:
                payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
                card_details = {
                    'last4': payment_method.card.last4,
                    'exp_month': payment_method.card.exp_month,
                    'exp_year': payment_method.card.exp_year,
                    'brand': payment_method.card.brand,
                    'country': payment_method.card.country,
                }
            else:
                card_details = None
                


            return Response({'client_secret': payment_intent , 'card_details': card_details}, status=status.HTTP_201_CREATED)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_400_BAD_REQUEST)


# class Manage_Cards(APIView):
#     def post(self, request):
#         data = request.data
#         try:
#             required_fields = ['customer_id', 'card_name', 'exp_year', 'exp_month', 'cvc', 'token']
#             for field in required_fields:
#                 if not data.get(field):
#                     raise ValidationError(f'{field.capitalize()} is required')

#             customer_id = data.get('customer_id')
#             customer = Customers.objects.get(stripe_customer_id=customer_id)
            
#             # Create a card using the token provided by Stripe.js or Stripe Elements
#             stripe.api_key = settings.STRIPE_SECRET_KEY
#             card = stripe.Customer.create_source(
#                 customer.stripe_customer_id,
#                 source=data.get('token')
#             )

#             card_number = card.last4
#             card = Cards.objects.create(
#                 customer=customer,
#                 card_name=data.get('card_name'),
#                 card_number=card_number,
#                 exp_year=data.get('exp_year'),
#                 exp_month=data.get('exp_month'),
#                 cvc=data.get('cvc')
#             )

#             return Response({'message': 'Card added successfully'}, status=status.HTTP_201_CREATED)
#         except Customers.DoesNotExist:
#             return Response({'error': 'Customer not found'}, status=status.HTTP_400_BAD_REQUEST)
#         except stripe.error.CardError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except IntegrityError:
#             return Response({'error': 'Card number already exists'}, status=status.HTTP_400_BAD_REQUEST)
        


class CreateCard(APIView):
    def get(self, request):
        cards = Cards.objects.all()
        serialized_cards = []
        for card in cards:
            serialized_card = {
                'card_number': card.card_number,
                'card_name': card.card_name,
                'exp_year': card.exp_year
            }
            serialized_cards.append(serialized_card)
        return Response({'cards': serialized_cards}, status=status.HTTP_200_OK)
 

    def post(self, request):
        data = request.data
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            required_fields = ['customer_id', 'stripe_token', 'card_name', 'exp_year', 'exp_month', 'cvc']
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

            cvc = str(data.get('cvc'))  
            if len(cvc) not in [3, 4]:
                return Response({'error': 'Invalid cvc length'}, status=status.HTTP_400_BAD_REQUEST)
            
            exp_year = str(data.get('exp_year'))
            if len(exp_year) != 4 or not exp_year.isdigit():
                return Response({'error': 'Invalid exp_year format'}, status=status.HTTP_400_BAD_REQUEST)

            exp_month = str(data.get('exp_month'))
            if len(exp_month) != 2 or not exp_month.isdigit() or int(exp_month) < 1 or int(exp_month) > 12:
                return Response({'error': 'Invalid exp_month format or out of range'}, status=status.HTTP_400_BAD_REQUEST)
            
            customer_id = data.get('customer_id')
            
            try:
                customer = Customers.objects.get(stripe_customer_id=customer_id)
            except Customers.DoesNotExist:
                return Response({'error': 'Customer does not exist.'}, status=status.HTTP_404_NOT_FOUND)
            
            card = stripe.Customer.create_source(
                customer_id,
                source=data.get('stripe_token')
            )

            print(card)
            customer_serializer = CustomersSerializer(customer)

            existing_card = Cards.objects.filter(card_number=card.last4).first()
            if existing_card:
                return Response({'error': 'Card already exists.'}, status=status.HTTP_409_CONFLICT)

            new_card = Cards.objects.create(
                customer=customer,
                card_name=data.get('card_name'),  
                card_number=card.last4, 
                exp_year=data.get('exp_year'),
                exp_month=data.get('exp_month'),
                cvc=data.get('cvc'),
                card_id=card.id
            )
            
            print(card)
            return Response({'message': 'Card added successfully', "card_id": card.id ,  'customer': customer_serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

