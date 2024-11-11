from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ServiceRequest


class CustomUserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_customer', 'is_service_provider', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_customer', 'is_service_provider', 'user_type')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'user_type', 'is_customer', 'is_service_provider')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'user_type')}
         ),
    )

    # Overriding the get_queryset method to include custom filters
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


# Admin class for ServiceRequest model
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'time', 'urgency_level', 'service_provider')
    list_filter = ('category', 'status', 'urgency_level')
    search_fields = ('user__email', 'category', 'description', 'location')
    ordering = ('-time',)
    readonly_fields = ('time',)
    autocomplete_fields = ['user', 'service_provider']

    fieldsets = (
        (None, {
            'fields': ('user', 'service_provider', 'category', 'description', 'status', 'urgency_level')
        }),
        ('Additional Info', {
            'fields': ('estimated_cost', 'media', 'location', 'time')
        }),
    )

    # Optional: to customize the queryset and restrict non-staff users' access
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)


# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
