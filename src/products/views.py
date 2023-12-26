# Django Import
import os
import uuid
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework Import
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

# Project level imports
from common.permissions import IsSuperUser
from .serializers import CreateProductSerializer, ProductSerializer
from .models import Product

# View to upload images.
class UploadProductImageView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    parser_classes = [MultiPartParser,]

    def post(self, request, *args, **kwargs):
        img = request.data["image"]
        img_name = os.path.splitext(img.name)[0]
        img_extension = os.path.splitext(img.name)[1]

        save_path = "media/posts/post_images/"
        if not os.path.exists(save_path):
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

        image_name = img_name + str(uuid.uuid4())
        img_save_path = "%s/%s%s" % (save_path, image_name, img_extension)
        response_url = "posts/post_images/" + image_name + img_extension
        with open(img_save_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)
        return Response({
            "path": response_url
        }, status=status.HTTP_200_OK)

class ListCreateProductView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "tags__title"]
    ordering_fields = ["created_at", "updated_at", "id"]
    ordering = ["-created_at"]
    page_size = 3
    pagination_class = PageNumberPagination

    filterset_fields = {
        "tags__title": ["exact", "in"],
        "created_at": ["exact", "gte", "lte"],
        "price": ["exact", "gte", "lte"]
    }

    def list(self, request, *args, **kwargs):
        self.pagination_class.page_size = self.page_size
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request and self.request.method == "POST":
            return CreateProductSerializer
        return ProductSerializer
    
    def get_queryset(self):
        products = Product.objects.filter().prefetch_related("tags")
        return products
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={
            "request": request
        })

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                "payload": serializer.data,
                "status": "success",
                "message": "successfully created"
            },
            status=status.HTTP_201_CREATED, headers=headers)