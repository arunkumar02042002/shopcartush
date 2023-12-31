from django.db import models
from common.models import TimeStampedModel
from django.contrib.auth import get_user_model
import uuid
from .choices import OrderStatus
from products.models import Product

User = get_user_model()

# Create your models here.
class Order(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    provider_order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(choices=OrderStatus.CHOICES_LIST, max_length=16)


class OrderItem(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveBigIntegerField()