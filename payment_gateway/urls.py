from django.urls import path
from . import views
from .views import  *
 

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('customers/', ManageCustomer.as_view(), name='customer-list-create'),
    path('add-card/', CreateCard.as_view(), name='process_payment'),
    path('customers/<int:customer_id>/', ManageCustomer.as_view(), name='customer-detail'),
    path('create-payment-intent/', CreatePaymentIntent.as_view(), name='create_payment_intent'),
    path('confirm-payment-intent/', ConfirmPaymentIntent.as_view(), name='confirm_payment_intent'),
    path('confirmation/', ConfirmationView.as_view(), name='payment_confirmation'),


    

]
