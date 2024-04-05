from django.urls import path
from . import views
from .views import  *
 

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    # customers
    path('customers/', ManageCustomer.as_view(), name='customer-list-create'),
    path('customers/<int:customer_id>/', ManageCustomer.as_view(), name='card-detail'),
    # card
    path('card/', ManageCard.as_view(), name='process_payment'),
    path('card/<int:card_id>/', ManageCard.as_view(), name='customer-detail'),
    # payment intent
    path('create-payment-intent/', CreatePaymentIntent.as_view(), name='create_payment_intent'),
    path('confirm-payment-intent/', ConfirmPaymentIntent.as_view(), name='confirm_payment_intent'),
    # Payment successfully URL
    path('confirmation/', ConfirmationView.as_view(), name='payment_confirmation'),
    # products
    path('products/', ManageProduct.as_view(), name='add-product'),
    path('products/<int:product_id>/', ManageProduct.as_view(), name='product-detail'),
]