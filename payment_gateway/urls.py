from django.urls import path
from . import views
from .views import Manage_Customer , Add_Card
 

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('customers/', Manage_Customer.as_view(), name='customer-list-create'),
    path('Add_Card/', Add_Card.as_view(), name='process_payment'),
]
