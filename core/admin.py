# core/admin.py  ← FINAL 100% CLEAN VERSION (NO DUPLICATE!)
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Student, RegularPassenger, Driver, Trip, Booking

# Clean User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models normally
admin.site.register(Student)
admin.site.register(RegularPassenger)
admin.site.register(Trip)
admin.site.register(Booking)

# ONLY ONE DRIVER REGISTRATION — WITH DECORATOR
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('driver_id', 'get_full_name', 'phone', 'is_approved', 'license_number')
    list_editable = ('is_approved',)
    search_fields = ('driver_id', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('driver_id',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Driver Name'

    fieldsets = (
        ('Driver Information', {
            'fields': ('user', 'phone', 'license_number', 'photo', 'is_approved')
        }),
        ('Auto-Generated ID', {
            'fields': ('driver_id',),
            'description': 'Automatically generated like DRV-NGR-0001'
        }),
    )