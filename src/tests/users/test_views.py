from rest_framework import status
import pytest
from orders.choices import OrderStatus
from users.models import Cart, CartItem
# import requests_mock
from orders.models import Order
from decimal import Decimal
import users

@pytest.mark.django_db(reset_sequences=True)
class TestAddToCartView:
    endpoint = "/addtocart/"

    def test_unauthenticated_users(self, create_unauthenticated_client):
        client = create_unauthenticated_client()
        url = self.endpoint
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "request_id, request_params, error_message",
        [
            (1, {}, "product_uuid: This field is required."),
            (2, {
                "product_uuid": "1233"
            }, "product_uuid: Must be a valid UUID.")
        ]
    )

    def test_response_is_400_when_request_params_incorrect(self, create_authenticated_client, create_user, request_id, request_params, error_message):
        user = create_user("1@2.com")
        client = create_authenticated_client(user)
        url = self.endpoint
        data = request_params
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["status"] == "error"
        assert response.data["message"] == error_message

    def test_success_if_cart_exists(self, create_authenticated_client, create_user, create_product):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 1

    def test_success_if_cart_not_exists(self, create_authenticated_client, create_user, create_product):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 1

    def test_product_does_not_exists(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        data = {
            "product_uuid": "1865c841-2494-46ee-9582-cbefa89078ca"
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["status"] == "error"
        assert response.data["message"] == "Product not found"

    def test_product_already_exist_in_cart(self, create_product, create_user, create_authenticated_client):
        admin_user = create_user('admin@gmail.com', is_superuser=True, is_staff=True)
        product = create_product(admin_user=admin_user)
        user = create_user('1@2gmail.com')
        cart = Cart.objects.create(
            user=user
        )
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product
        )
        data = {
            "product_uuid": str(product.uuid)
        }
        url = self.endpoint
        client = create_authenticated_client(user=user)
        response = client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        carts = Cart.objects.all()
        assert carts.count() == 1
        assert carts.first().user == user
        cart_items = carts.first().items
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 2