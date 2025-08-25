from django.contrib import admin
from .models import TravelInfo, UserProfile, Notification, Follow, Comments
# Register your models here.
admin.site.register(TravelInfo)
admin.site.register(UserProfile)
admin.site.register(Notification)
admin.site.register(Follow)
admin.site.register(Comments)