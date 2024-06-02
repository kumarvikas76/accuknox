from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, FriendRequest

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    list_display = ('id','email', 'name', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(CustomUser, UserAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'status', 'created_at','updated_at')
    search_fields = ('sender__name', 'recipient__name')
    list_filter = ('status', 'created_at')

admin.site.register(FriendRequest, FriendRequestAdmin)