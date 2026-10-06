from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notifications'),
    path('<int:notif_id>/read/', views.mark_read, name='mark_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('clear/', views.clear_all_notifications, name='clear_notifications'),
]
