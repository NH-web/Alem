from django.contrib import admin
from .models import TemporaryMemory

@admin.register(TemporaryMemory)
class TemporaryMemoryAdmin(admin.ModelAdmin):
    list_display = (
        'phone',
        'code',
        'created_at',
        'verified_status',
        'expired_status',
    )

    list_filter = ('created_at', 'code_verified')
    search_fields = ('phone',)

    # ✅ Admin helper methods
    def verified_status(self, obj):
        return obj.code_verified
    verified_status.boolean = True
    verified_status.short_description = "Verified"

    def expired_status(self, obj):
        return obj.code_expired
    expired_status.boolean = True
    expired_status.short_description = "Expired"
