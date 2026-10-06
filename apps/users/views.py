from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .forms import CustomerRegistrationForm, ManagerRegistrationForm, CustomLoginForm, ManagerProfileUpdateForm
from .models import CustomUser, ManagerProfile, Review
from apps.events.models import Event
from apps.bidding.models import Bid
from apps.notifications.models import Notification


def register_customer(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Your account has been created.')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'users/register_customer.html', {'form': form})


def register_manager(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Your manager profile is ready.')
            return redirect('manager_dashboard')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'users/register_manager.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin_user():
        return redirect('admin_dashboard')
    elif user.is_manager():
        return redirect('manager_dashboard')
    else:
        return redirect('customer_dashboard')


@login_required
def customer_dashboard(request):
    if not request.user.is_customer():
        return redirect('dashboard')
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    stats = {
        'total_events': events.count(),
        'open_events': events.filter(status='open').count(),
        'assigned_events': events.filter(status='assigned').count(),
        'completed_events': events.filter(status='completed').count(),
    }
    recent_events = events[:5]
    unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'users/customer_dashboard.html', {
        'events': recent_events,
        'stats': stats,
        'unread_notifications': unread_notifications,
    })


@login_required
def manager_dashboard(request):
    if not request.user.is_manager():
        return redirect('dashboard')
    try:
        profile = request.user.manager_profile
    except ManagerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your manager profile.')
        return redirect('update_profile')

    my_bids = Bid.objects.filter(manager=request.user).select_related('event')
    stats = {
        'total_bids': my_bids.count(),
        'pending_bids': my_bids.filter(status='pending').count(),
        'accepted_bids': my_bids.filter(status='accepted').count(),
        'completed_events': profile.completed_events,
        'trust_score': profile.trust_score,
        'average_rating': profile.average_rating,
    }
    available_events = Event.objects.filter(status='open').exclude(
        bids__manager=request.user
    ).order_by('-created_at')[:5]
    recent_bids = my_bids.order_by('-created_at')[:5]
    unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'users/manager_dashboard.html', {
        'profile': profile,
        'stats': stats,
        'available_events': available_events,
        'recent_bids': recent_bids,
        'unread_notifications': unread_notifications,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    from apps.events.models import Category
    stats = {
        'total_users': CustomUser.objects.count(),
        'customers': CustomUser.objects.filter(role='customer').count(),
        'managers': CustomUser.objects.filter(role='manager').count(),
        'total_events': Event.objects.count(),
        'open_events': Event.objects.filter(status='open').count(),
        'completed_events': Event.objects.filter(status='completed').count(),
        'total_bids': Bid.objects.count(),
        'categories': Category.objects.count(),
    }
    recent_events = Event.objects.order_by('-created_at')[:10]
    recent_users = CustomUser.objects.order_by('-date_joined')[:10]
    return render(request, 'users/admin_dashboard.html', {
        'stats': stats,
        'recent_events': recent_events,
        'recent_users': recent_users,
    })


@login_required
def update_profile(request):
    if not request.user.is_manager():
        messages.error(request, 'Only managers can update profiles.')
        return redirect('dashboard')
    profile, created = ManagerProfile.objects.get_or_create(
        user=request.user,
        defaults={'location': request.user.city or 'Not set', 'services_offered': 'General Services'}
    )
    if request.method == 'POST':
        form = ManagerProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.calculate_trust_score()
            messages.success(request, 'Profile updated successfully!')
            return redirect('manager_dashboard')
    else:
        form = ManagerProfileUpdateForm(instance=profile)
    return render(request, 'users/update_profile.html', {'form': form, 'profile': profile})


@login_required
def manager_profile_view(request, manager_id):
    manager = get_object_or_404(CustomUser, id=manager_id, role='manager')
    profile = get_object_or_404(ManagerProfile, user=manager)
    reviews = Review.objects.filter(manager=manager).select_related('reviewer', 'event').order_by('-created_at')
    return render(request, 'users/manager_profile.html', {
        'manager': manager,
        'profile': profile,
        'reviews': reviews,
    })


@login_required
def submit_review(request, event_id):
    from apps.events.models import Event
    event = get_object_or_404(Event, id=event_id, organizer=request.user, status='completed')
    if Review.objects.filter(reviewer=request.user, event=event).exists():
        messages.warning(request, 'You have already reviewed this event.')
        return redirect('event_detail', pk=event_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        if event.assigned_manager and 1 <= rating <= 5:
            review = Review.objects.create(
                reviewer=request.user,
                manager=event.assigned_manager,
                event=event,
                rating=rating,
                comment=comment
            )
            # Update manager's average rating
            profile = event.assigned_manager.manager_profile
            avg = Review.objects.filter(manager=event.assigned_manager).aggregate(Avg('rating'))['rating__avg']
            profile.average_rating = round(avg, 2)
            profile.save(update_fields=['average_rating'])
            profile.calculate_trust_score()
            # Notify manager
            from apps.notifications.models import create_notification
            create_notification(
                recipient=event.assigned_manager,
                notification_type='new_review',
                title='New Review Received',
                message=f'{request.user.username} left a {rating}-star review for "{event.title}".',
                link=f'/users/manager/{event.assigned_manager.id}/'
            )
            messages.success(request, 'Review submitted successfully!')
        return redirect('event_detail', pk=event_id)
    return render(request, 'users/submit_review.html', {'event': event})


@login_required
def manage_users(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    users = CustomUser.objects.all().order_by('-date_joined')
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'users/manage_users.html', {'users': users, 'role_filter': role_filter})


@login_required
def toggle_user_active(request, user_id):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('manage_users')
