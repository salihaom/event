import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Event, Category, EventTemplate
from .forms import EventForm
from apps.notifications.models import create_notification


def home(request):
    categories = Category.objects.all()
    recent_events = Event.objects.filter(status='open').order_by('-created_at')[:6]
    stats = {
        'events': Event.objects.count(),
        'managers': 0,
        'categories': categories.count(),
    }
    try:
        from apps.users.models import ManagerProfile
        stats['managers'] = ManagerProfile.objects.filter(is_available=True).count()
    except Exception:
        pass
    return render(request, 'events/home.html', {
        'categories': categories,
        'recent_events': recent_events,
        'stats': stats,
    })


@login_required
def create_event(request):
    if not request.user.is_customer():
        messages.error(request, 'Only customers can create events.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
        category_id = request.GET.get('category')
        if category_id:
            try:
                template = EventTemplate.objects.get(category_id=category_id)
                form.initial['category'] = category_id
                form.template_suggestion = template
            except EventTemplate.DoesNotExist:
                pass
    templates = EventTemplate.objects.select_related('category').all()
    return render(request, 'events/create_event.html', {
        'form': form,
        'templates': templates,
    })


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.is_customer() and event.organizer != request.user:
        messages.error(request, 'You can only view your own events.')
        return redirect('customer_dashboard')
    bids = event.bids.select_related('manager', 'manager__manager_profile').order_by('-recommendation_score')
    best_bid = event.get_best_bid()
    # Recalculate scores for all bids
    for bid in bids:
        bid.calculate_recommendation_score()
    bids = event.bids.select_related('manager', 'manager__manager_profile').order_by('-recommendation_score')

    # Apply filters
    sort_by = request.GET.get('sort', '')
    location_filter = request.GET.get('location', '')
    if sort_by == 'price_low':
        bids = bids.order_by('price')
    elif sort_by == 'price_high':
        bids = bids.order_by('-price')
    elif sort_by == 'rating':
        bids = bids.order_by('-manager__manager_profile__average_rating')
    elif sort_by == 'trust':
        bids = bids.order_by('-manager__manager_profile__trust_score')
    if location_filter:
        bids = bids.filter(manager__manager_profile__location__icontains=location_filter)

    has_reviewed = False
    if request.user.is_customer() and event.status == 'completed':
        from apps.users.models import Review
        has_reviewed = Review.objects.filter(reviewer=request.user, event=event).exists()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'bids': bids,
        'best_bid': best_bid,
        'sort_by': sort_by,
        'location_filter': location_filter,
        'has_reviewed': has_reviewed,
    })


@login_required
def event_list_customer(request):
    if not request.user.is_customer():
        return redirect('dashboard')
    events = Event.objects.filter(organizer=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        events = events.filter(status=status_filter)
    return render(request, 'events/event_list_customer.html', {
        'events': events,
        'status_filter': status_filter,
        'status_choices': Event.STATUS_CHOICES,
    })


@login_required
def event_list_manager(request):
    if not request.user.is_manager():
        return redirect('dashboard')
    events = Event.objects.filter(status='open').exclude(bids__manager=request.user)
    budget_min = request.GET.get('budget_min', '')
    budget_max = request.GET.get('budget_max', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')

    if budget_min:
        events = events.filter(budget__gte=budget_min)
    if budget_max:
        events = events.filter(budget__lte=budget_max)
    if location:
        events = events.filter(location__icontains=location)
    if category:
        events = events.filter(category_id=category)

    categories = Category.objects.all()
    return render(request, 'events/event_list_manager.html', {
        'events': events,
        'categories': categories,
        'filters': {
            'budget_min': budget_min,
            'budget_max': budget_max,
            'location': location,
            'category': category,
        }
    })


@login_required
def update_event_status(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_transitions = {
            'open': ['in_review', 'cancelled'],
            'in_review': ['open', 'assigned', 'cancelled'],
            'assigned': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
        }
        if new_status in valid_transitions.get(event.status, []):
            event.status = new_status
            event.save()
            if new_status == 'completed' and event.assigned_manager:
                profile = event.assigned_manager.manager_profile
                profile.completed_events += 1
                profile.save(update_fields=['completed_events'])
                profile.calculate_trust_score()
            messages.success(request, f'Event status updated to "{new_status}".')
        else:
            messages.error(request, 'Invalid status transition.')
    return redirect('event_detail', pk=pk)


@login_required
def manage_categories(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    categories = Category.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            icon = request.POST.get('icon', '🎉')
            desc = request.POST.get('description', '')
            if name:
                Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
                messages.success(request, f'Category "{name}" added.')
        elif action == 'delete':
            cat_id = request.POST.get('cat_id')
            Category.objects.filter(id=cat_id).delete()
            messages.success(request, 'Category deleted.')
    return render(request, 'events/manage_categories.html', {'categories': categories})


@login_required
def all_events_admin(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    events = Event.objects.select_related('organizer', 'category', 'assigned_manager').order_by('-created_at')
    return render(request, 'events/all_events_admin.html', {'events': events})


@login_required
def budget_optimizer(request):
    if not request.user.is_customer():
        return redirect('dashboard')
    suggestions = []
    event_id = request.GET.get('event_id')
    if event_id:
        event = get_object_or_404(Event, pk=event_id, organizer=request.user)
        bids = event.bids.filter(status='pending').select_related('manager', 'manager__manager_profile')
        budget = float(event.budget)
        within_budget = [b for b in bids if float(b.price) <= budget]
        within_budget.sort(key=lambda b: b.recommendation_score, reverse=True)
        suggestions = within_budget[:3]
        return render(request, 'events/budget_optimizer.html', {
            'event': event,
            'suggestions': suggestions,
            'budget': budget,
        })
    events = Event.objects.filter(organizer=request.user, status__in=['open', 'in_review'])
    return render(request, 'events/budget_optimizer.html', {'events': events})
