import re
from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views import View
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
from .serializers import CardSerializer, CustomersSerializer , ProductsSerializer
from decimal import Decimal
from django.urls import reverse
from datetime import datetime
# from .renderers import ErrorRenderer


stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    session_id = "cs_test_a1pMtJRsTGOg3t17dGDsjOONvmDWZ63PCFL7lYBCwo3pnFRWTl4cAk0Cba"
    return render(request, 'index.html', {'session_id': session_id})

# Customer Related View 
class ManageCustomer(APIView):

    def get(self, request, customer_id=None):
        if customer_id is not None:
            try:
                customer = Customers.objects.get(id=customer_id)
                serializer = CustomersSerializer(customer)
                return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
            except Products.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            customer = Customers.objects.all()
            serializer = CustomersSerializer(customer, many=True)
            return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
    
    def post(self, request):
        data = request.data
        errors = []
        try:
            required_fields = ['email', 'name']
            for field in required_fields:
                if not data.get(field):
                    errors.append({'error': f'{field} is required'})

            if errors:
                  return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': errors}, status=status.HTTP_400_BAD_REQUEST)

            customer = stripe.Customer.create(
                email=data.get('email'),
                name=data.get('name'),
            )

            try:
                customer_entry = Customers.objects.create(
                    name=data.get('name'),
                    email=data.get('email'),
                    stripe_customer_id=customer.id,
                )
                return Response({'customer': customer}, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': 'Customer with the same name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def patch(self, request, customer_id):
        try:
            customer = Customers.objects.get(id=customer_id)
            serializer = CustomersSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': status.HTTP_200_OK, 'success': True, 'message': 'Customer details updated successfully'})
            else:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Customers.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False, 'errors': {'detail': 'Customer not found'}}, status=status.HTTP_404_NOT_FOUND)
        
        
    def delete(self, request, customer_id, format=None):
        try:
            customer = Customers.objects.get(id=customer_id)
            customer.delete()
            return Response({'status': status.HTTP_204_NO_CONTENT, 'success': True ,'message' : 'customer  successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False, 'errors': {'detail': 'customer not found'}})

# PaymentIntent Related View 
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
            return_url = 'http://127.0.0.1:3000/confirmation/'

            customer_id = data.get('customer_id')
            customer = stripe.Customer.retrieve(customer_id)

            card_id = data.get('card_id')
            payment_method = stripe.PaymentMethod.retrieve(card_id)

            payment_method.attach(customer=customer_id)

            payment_intent = stripe.PaymentIntent.create(
                amount=price,
                currency='INR',
                customer=data.get('customer_id'),
                payment_method=data.get('card_id') ,
                metadata={'product_id': data.get('product_id'), 'quantity': data.get('quantity')},
                confirm=True, 
                return_url=return_url
            )
            print('=-=-=-=-',payment_intent.id)
           
            print('Payment Intent:', payment_intent)

            return Response({'status': status.HTTP_200_OK, 'success': True ,'client_secret': payment_intent }, status=status.HTTP_201_CREATED)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_400_BAD_REQUEST)

# Confirm PaymentIntent Related View 
class ConfirmPaymentIntent(APIView):
    def post(self, request):
        data = request.data
        try:
            required_fields = ['card_id', 'payment_intent_id']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field.capitalize()} is required')

            stripe.api_key = settings.STRIPE_SECRET_KEY

            payment_intent = stripe.PaymentIntent.confirm(
                data.get('payment_intent_id'),
                payment_method=data.get('card_id'),
                return_url='http://127.0.0.1:3000/confirmation/' 
            )

            return Response({'message': 'Payment Intent confirmed successfully','payment_intent' : payment_intent}, status=status.HTTP_200_OK)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Payment confirmed  URL
class ConfirmationView(APIView):
    def get(self, request):
        return HttpResponse("Payment confirmed successfully")
    

# Card Related View 
class ManageCard(APIView):
    def get(self, request, card_id=None): 
        print('=-=-=-==-=-==', card_id)
        if card_id is not None:
            try:
                card = Cards.objects.get(id=card_id)
                serializer = CardSerializer(card)
                return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
            except Cards.DoesNotExist:
                return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            card = Cards.objects.all()
            serializer = CardSerializer(card, many=True)
            return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
 

    def post(self, request):
        data = request.data
        errors = []
        customer = None
        
        try:
            # Required Fields 
            required_fields = ['customer_id', 'card_number', 'card_name', 'exp_year', 'exp_month', 'cvc']
            for field in required_fields:
                if field not in data:
                    errors.append({'error': f'{field} is required'})

            # CVC   
            cvc = str(data.get('cvc'))  
            if len(cvc) != 3:
                errors.append({'cvc': 'CVC must be 3 characters long'})

            # Exp Year
            exp_year = str(data.get('exp_year'))
            if not exp_year.isdigit() or len(exp_year) != 4:
                errors.append({'exp_year': 'exp_year must be a 4-digit number'})
            else:
                current_year = datetime.now().year
                if int(exp_year) < current_year:
                    errors.append({'exp_year': 'Expiration year must be in the future'})

            # Exp Month
            exp_month = str(data.get('exp_month'))
            if not exp_month.isdigit() or int(exp_month) < 1 or int(exp_month) > 12:
                errors.append({'exp_month': 'exp_month must be a number between 1 and 12'})

            # Stripe Token
            stripe_token = data.get('card_number')
            if not stripe_token or not isinstance(stripe_token, str):
                errors.append({'card_number': 'Invalid or missing stripe token'})

            # Card Name
            card_name = data.get('card_name')
            if not  card_name:
                errors.append({'error': 'Card Name is required'})

            # Coustomer Id    
            customer_id = data.get('customer_id')
            
            try:
                customer = Customers.objects.get(stripe_customer_id=customer_id)
            except Customers.DoesNotExist:
                errors.append({'customer': 'Customer does not exist.'})

            # Card limit
            existing_cards_count = Cards.objects.filter(customer=customer).count()
            if existing_cards_count >= 2:
                errors.append({'customer': 'Card limit reached for this customer.'})
            
            if errors:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': errors} ,status=status.HTTP_400_BAD_REQUEST)
            
            try:
                card = stripe.Customer.create_source(
                    customer_id,
                    source=data.get('card_number')
                )
            except stripe.error.CardError as e:
                if e.code == 'card_not_supported':
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': 'Your card is not supported.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            customer_serializer = CustomersSerializer(customer)

            existing_card = Cards.objects.filter(card_number=card.last4).first()
            if existing_card:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False , 'error': 'Card already exists.'}, status=status.HTTP_409_CONFLICT)

            new_card = Cards.objects.create(
                customer=customer,
                card_name=data.get('card_name'),  
                card_number=card.last4, 
                exp_year=data.get('exp_year'),
                exp_month=data.get('exp_month'),
                cvc=data.get('cvc'),
                card_id=card.id
            )
            
            return Response({'status': status.HTTP_200_OK, 'success': True ,'message': 'Card added successfully', "card_id": card.id ,  'customer': customer_serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            if customer is None:
                errors.append({'error': 'Failed to process request.'})
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, card_id):
        try:
            card = Cards.objects.get(id=card_id)
            serializer = CardSerializer(card, data=request.data, partial=True)
            if serializer.is_valid():
                if 'cvc' not in request.data:
                    serializer.validated_data['cvc'] = card.cvc
                    
                current_year = datetime.now().year
                exp_year = serializer.validated_data.get('exp_year')
                exp_month = serializer.validated_data.get('exp_month')
                
                if exp_month is not None and (not isinstance(exp_month, int) or exp_month < 1 or exp_month > 12):
                    error_message = 'Expiration month must be a number between 1 and 12'
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'exp_month': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                
                if exp_year is not None and (not isinstance(exp_year, int) or len(str(exp_year)) != 4):
                    error_message = 'Expiration year must be a valid 4-digit number'
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'exp_year': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                elif exp_year and exp_year < current_year:
                    error_message = 'Expiration year must be in the future'
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'exp_year': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                
                if 'card_number' in serializer.validated_data:
                    error_message = 'Cannot update card number'
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'card_number': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                return Response({'status': status.HTTP_200_OK, 'success': True, 'message': 'Card details updated successfully'})
            else:
                exp_year_errors = serializer.errors.get('exp_year')
                exp_month_errors = serializer.errors.get('exp_month')
                if exp_year_errors and "Ensure this value is less than or equal to 65535." in exp_year_errors:
                    error_message = "Expiration year must be a valid 4-digit number"
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'exp_year': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                elif exp_month_errors and "Ensure this value is less than or equal to 65535." in exp_month_errors:
                    error_message = "Expiration month must be a number between 1 and 12"
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'exp_month': [error_message]}}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Cards.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False, 'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)

    
    def delete(self, request, card_id, format=None):
        try:
            card = Cards.objects.get(id=card_id)
            card.delete()
            return Response({'status': status.HTTP_204_NO_CONTENT, 'success': True ,'message' : 'Delete card successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False, 'errors': {'detail': 'card not found'}})
        

# Product Related View 
class ManageProduct(APIView):
    def get(self, request, product_id=None):
        if product_id is not None:
            try:
                product = Products.objects.get(id=product_id)
                serializer = ProductsSerializer(product)
                return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
            except Products.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = Products.objects.all()
            serializer = ProductsSerializer(products, many=True)
            return Response({'status': status.HTTP_200_OK, 'success': True, 'data': serializer.data})
    
    def post(self, request):
        serializer = ProductsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': status.HTTP_201_CREATED, 'success': True, 'data': serializer.data})
        return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False ,  'data': serializer.errors} , status=status.HTTP_400_BAD_REQUEST)  
    
    def patch(self, request, product_id):
        try:
            product = Products.objects.get(id=product_id)
            serializer = ProductsSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                if serializer.validated_data:  
                    serializer.save()
                    return Response({'status': status.HTTP_200_OK, 'success': True, 'message': 'product details updated successfully'})
                else:  
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'detail': 'No product to update'}},status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'errors': {'detail': 'product not found'}})
        
    def delete(self, request, product_id, format=None):
        try:
            product = Products.objects.get(id=product_id)
            product.delete()
            return Response({'status': status.HTTP_204_NO_CONTENT, 'success': True ,'message' : 'Delete product successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'success': False, 'errors': {'detail': 'product not found'}})
    
    

