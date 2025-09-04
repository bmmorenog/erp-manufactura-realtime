from django.contrib import admin
from .models import OperationalCenter

@admin.register(OperationalCenter)
class OperationalCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'city', 'regional', 'center_type', 'status', 'last_sync_at']
    list_filter = ['status', 'center_type', 'regional', 'city']
    search_fields = ['code', 'name', 'city', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('code', 'name', 'center_type', 'status')
        }),
        ('Location', {
            'fields': ('regional', 'city', 'address', 'latitude', 'longitude')
        }),
        ('Cross References', {
            'fields': ('branch_reference', 'headquarters_reference', 'rtm_reference'),
            'classes': ('collapse',)
        }),
        ('Operations', {
            'fields': ('operation_type', 'cameras', 'rtm_schedule', 'ac_schedule')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_sync_at'),
            'classes': ('collapse',)
        })
    )
