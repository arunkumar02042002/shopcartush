from django.contrib import admin
from .models import Product, ProductTag, Tag

# Register your models here.
admin.site.register(ProductTag)
admin.site.register(Product)
admin.site.register(Tag)
