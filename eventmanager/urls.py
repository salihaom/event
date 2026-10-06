"""URL Configuration for Event Management System"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events import views as event_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', event_views.home, name='home'),
    path('users/', include('apps.users.urls')),
    path('events/', include('apps.events.urls')),
    path('bidding/', include('apps.bidding.urls')),
    path('notifications/', include('apps.notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
