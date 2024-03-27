from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import stripe
from rest_framework import generics
from .models import Customers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from django.core.exceptions import ValidationError


stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    session_id = "cs_test_a1y90yGmU8Z1kiL70QEtE5kNoHQkz2ITf1j8JzQNkd3FgSsNV2IPYYC9n2"
    return render(request, 'index.html', {'session_id': session_id})



class Create_Customer(APIView):
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
            return Response({'customer': customer}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        