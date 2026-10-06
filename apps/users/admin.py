from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ManagerProfile, Review


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'phone', 'city')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role', 'phone', 'city')}),
    )


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'trust_score', 'average_rating', 'completed_events']
    list_filter = ['is_available']
    search_fields = ['user__username', 'location', 'services_offered']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'manager', 'event', 'rating', 'created_at']
    list_filter = ['rating']
