from django.urls import path
from users.views import PlaceOrderView

urlpatterns = [
    path('', PlaceOrderView.as_view(), name="place_order"),
]