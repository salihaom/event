from django.urls import path
from . import views

urlpatterns = [
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/manager/', views.register_manager, name='register_manager'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('manager/<int:manager_id>/', views.manager_profile_view, name='manager_profile'),
    path('review/<int:event_id>/', views.submit_review, name='submit_review'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
]
