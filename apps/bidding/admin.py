from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['event', 'manager', 'price', 'status', 'recommendation_score', 'created_at']
    list_filter = ['status']
    search_fields = ['event__title', 'manager__username']
