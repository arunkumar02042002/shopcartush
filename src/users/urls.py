from django.urls import path
from . import views

urlpatterns = [
    path('addtocart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', view=views.DisplayCartView.as_view(), name='display_cart')
]