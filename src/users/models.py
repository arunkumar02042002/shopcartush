from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel
from products.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="carts")

    def __str__(self) -> str:
        return 'user-'+str(self.user_id)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'cart_id'], name='unique_cart_product'
            )
        ]

    def __str__(self) -> str:
        return 'cart_'+str(self.cart_id)+ '-product-'+str(self.product_id)