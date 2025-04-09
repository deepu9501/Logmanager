"""
Admin configuration for the users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    list_display = ('username', 'email', 'role', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'department')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', 'phone', 'department')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'notification_email', 'notification_sms')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'department')
    ordering = ('username',)
    change_user_password_template = None

class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserActivity model.
    """
    list_display = ('user', 'action', 'object_type', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'object_type', 'created_at')
    search_fields = ('user__username', 'action', 'object_type', 'ip_address')
    readonly_fields = ('user', 'action', 'object_type', 'object_id', 'ip_address', 'details', 'created_at')
    ordering = ('-created_at',)

admin.site.register(UserActivity, UserActivityAdmin) 