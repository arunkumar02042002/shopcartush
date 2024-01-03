from django.contrib import admin
from .models import Notification, ScheduledNotification

# Register your models here.
admin.site.register(Notification)
admin.site.register(ScheduledNotification)