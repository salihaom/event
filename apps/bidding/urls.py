from django.urls import path
from . import views

urlpatterns = [
    path('place/<int:event_id>/', views.place_bid, name='place_bid'),
    path('accept/<int:bid_id>/', views.accept_bid, name='accept_bid'),
    path('reject/<int:bid_id>/', views.reject_bid, name='reject_bid'),
    path('withdraw/<int:bid_id>/', views.withdraw_bid, name='withdraw_bid'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('admin/all/', views.all_bids_admin, name='all_bids_admin'),
]
