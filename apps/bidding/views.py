from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Bid
from apps.events.models import Event
from apps.notifications.models import create_notification


@login_required
def place_bid(request, event_id):
    if not request.user.is_manager():
        messages.error(request, 'Only managers can place bids.')
        return redirect('dashboard')
    event = get_object_or_404(Event, pk=event_id, status='open')
    if Bid.objects.filter(event=event, manager=request.user).exists():
        messages.warning(request, 'You have already placed a bid on this event.')
        return redirect('available_events')
    if request.method == 'POST':
        price = request.POST.get('price')
        proposal = request.POST.get('proposal', '')
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid price.')
            return redirect('place_bid', event_id=event_id)
        bid = Bid.objects.create(
            event=event,
            manager=request.user,
            price=price,
            proposal=proposal
        )
        bid.calculate_recommendation_score()
        # Notify customer
        create_notification(
            recipient=event.organizer,
            notification_type='new_bid',
            title='New Bid Received',
            message=f'{request.user.get_full_name() or request.user.username} placed a bid of ₹{price:,.0f} on your event "{event.title}".',
            link=f'/events/{event.pk}/'
        )
        messages.success(request, 'Bid placed successfully!')
        return redirect('manager_dashboard')
    try:
        manager_profile = request.user.manager_profile
    except Exception:
        manager_profile = None
    return render(request, 'bidding/place_bid.html', {
        'event': event,
        'manager_profile': manager_profile,
    })


@login_required
def accept_bid(request, bid_id):
    if not request.user.is_customer():
        messages.error(request, 'Only customers can accept bids.')
        return redirect('dashboard')
    bid = get_object_or_404(Bid, pk=bid_id, event__organizer=request.user, status='pending')
    event = bid.event
    # Reject all other bids
    other_bids = Bid.objects.filter(event=event).exclude(pk=bid_id)
    for other_bid in other_bids:
        other_bid.status = 'rejected'
        other_bid.save()
        create_notification(
            recipient=other_bid.manager,
            notification_type='bid_rejected',
            title='Bid Not Selected',
            message=f'Your bid for "{event.title}" was not selected. Better luck next time!',
            link=f'/events/{event.pk}/'
        )
    # Accept this bid
    bid.status = 'accepted'
    bid.save()
    event.assigned_manager = bid.manager
    event.status = 'assigned'
    event.save()
    # Notify winning manager
    create_notification(
        recipient=bid.manager,
        notification_type='bid_accepted',
        title='🎉 Bid Accepted!',
        message=f'Your bid for "{event.title}" has been accepted! Contact {request.user.get_full_name() or request.user.username} to proceed.',
        link=f'/events/{event.pk}/'
    )
    messages.success(request, f'Bid accepted! {bid.manager.get_full_name() or bid.manager.username} has been assigned to your event.')
    return redirect('event_detail', pk=event.pk)


@login_required
def reject_bid(request, bid_id):
    if not request.user.is_customer():
        messages.error(request, 'Only customers can reject bids.')
        return redirect('dashboard')
    bid = get_object_or_404(Bid, pk=bid_id, event__organizer=request.user, status='pending')
    bid.status = 'rejected'
    bid.save()
    create_notification(
        recipient=bid.manager,
        notification_type='bid_rejected',
        title='Bid Rejected',
        message=f'Your bid for "{bid.event.title}" has been rejected.',
        link=f'/events/{bid.event.pk}/'
    )
    messages.info(request, 'Bid rejected.')
    return redirect('event_detail', pk=bid.event.pk)


@login_required
def withdraw_bid(request, bid_id):
    if not request.user.is_manager():
        return redirect('dashboard')
    bid = get_object_or_404(Bid, pk=bid_id, manager=request.user, status='pending')
    bid.status = 'withdrawn'
    bid.save()
    messages.info(request, 'Bid withdrawn.')
    return redirect('manager_dashboard')


@login_required
def my_bids(request):
    if not request.user.is_manager():
        return redirect('dashboard')
    bids = Bid.objects.filter(manager=request.user).select_related('event', 'event__category').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bids = bids.filter(status=status_filter)
    return render(request, 'bidding/my_bids.html', {
        'bids': bids,
        'status_filter': status_filter,
        'status_choices': Bid.STATUS_CHOICES,
    })


@login_required
def all_bids_admin(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    bids = Bid.objects.select_related('event', 'manager').order_by('-created_at')
    return render(request, 'bidding/all_bids_admin.html', {'bids': bids})
