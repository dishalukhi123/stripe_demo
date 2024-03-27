from django.urls import path
from . import views
from .views import Create_Customer 
 

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('customers/', Create_Customer.as_view(), name='customer-list-create'),

]
