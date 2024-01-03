from django.urls import path, re_path
from products.views import UploadProductImageView, ListCreateProductView
from notifications.views import ScheduleNotificationView

urlpatterns = [
    path('products/', ListCreateProductView.as_view(), name='list-create-product'),
    path('products/image_upload/', UploadProductImageView.as_view(), name='product-image-upload'),
    path('notifications/', ScheduleNotificationView.as_view(), name='schedule-notification')
    # re_path(r'^(?P<version>(v1|v2))/products/$', ListCreateProductView.as_view(), name='list-create-product'),
]