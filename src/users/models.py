from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel
from products.models import Product

User = get_user_model()

# Create your models here.
class Cart(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name="carts")

class CartItem(models.Model):
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
