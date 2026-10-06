from django.contrib import admin
from .models import Category, Event, EventTemplate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'budget', 'location', 'event_date', 'status']
    list_filter = ['status', 'category']
    search_fields = ['title', 'organizer__username', 'location']
    date_hierarchy = 'event_date'


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'timeline_days', 'estimated_budget_min', 'estimated_budget_max']
