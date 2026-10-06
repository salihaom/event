from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/status/', views.update_event_status, name='update_event_status'),
    path('my-events/', views.event_list_customer, name='my_events'),
    path('available/', views.event_list_manager, name='available_events'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('all/', views.all_events_admin, name='all_events_admin'),
    path('budget-optimizer/', views.budget_optimizer, name='budget_optimizer'),
]
