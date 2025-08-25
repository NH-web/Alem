from django.contrib import admin
from .models import TemporaryMemory

@admin.register(TemporaryMemory)
class TemporaryMemoryAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_verified', 'is_expired','sent')
    list_filter = ('created_at','sent')
    search_fields = ('email',)


    # ✅ Add helper properties for admin
    def is_verified(self, obj):
        return not obj.code_expired
    is_verified.boolean = True  # ✅ show as a green/red icon

    def is_expired(self, obj):
        return obj.code_expired
    is_expired.boolean = True
