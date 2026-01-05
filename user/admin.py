from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailOTP, Agent
from django.contrib.auth.models import Group

admin.site.site_header = "iqtisodiybilim.uz Admin Dashboard"
admin.site.site_title = "iqtisodiybilim.uz Admin Dashboard"
admin.site.index_title = "Welcome to iqtisodiybilim.uz Admin Dashboard"
admin.site.empty_value_display = "None"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
        'last_login'
    )
    ordering = ('email',)
    filter_horizontal = ('user_permissions', 'groups',)
    list_filter = ('is_active', 'is_superuser', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    fieldsets = (
        ('Login', {
            'fields': ('email', 'password',),
            'classes': ('wide',),
        }),
        ("Personal Info", {
            'fields': ('first_name', 'last_name',),
            'classes': ('wide',),
        }),
        ("Additional Info", {
            'fields': ('profile_image', 'bio',),
            'classes': ('wide',),
        }),
        ("Permissions", {
            'fields': ('is_superuser', 'is_staff', 'is_active',),
            'classes': ('wide',),
        }),
        ("User Permissions and Groups", {
            'fields': ('groups', 'user_permissions',),
            'classes': ('wide',),
        }),
    )
    add_fieldsets = (
        ('Create Super User', {
            'fields': ('email',),
            'classes': ('wide',),
        }),
        ('Passwords', {
            'fields': ('password1', 'password2',),
            'classes': ('wide',),
        }),
        ("Permissions", {
            'fields': ('is_superuser', 'is_staff', 'is_active',),
            'classes': ('wide',),
        }),
        ("User Permissions and Groups", {
            'fields': ('groups', 'user_permissions',),
            'classes': ('wide',),
        }),
    )

# admin.site.unregister(Group)
admin.site.register(EmailOTP)
admin.site.register(Agent)
