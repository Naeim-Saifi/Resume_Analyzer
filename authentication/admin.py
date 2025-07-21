from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    #Edit the fieldsets to include the role field
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    #When adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'first_name', 'last_name', 'role')}),
    )

#Register the UserProfile model with the UserProfileAdmin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


admin.site.register(CustomUser, CustomUserAdmin)