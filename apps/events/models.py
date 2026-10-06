from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🎉')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class EventTemplate(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=200)
    description = models.TextField()
    suggested_services = models.TextField()
    timeline_days = models.PositiveIntegerField(default=30)
    estimated_budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_budget_max = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Event(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open for Bids'),
        ('in_review', 'Reviewing Bids'),
        ('assigned', 'Manager Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    event_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_bid_count(self):
        return self.bids.count()

    def get_best_bid(self):
        """Returns the bid with the highest recommendation score"""
        bids = self.bids.filter(status='pending').select_related('manager__manager_profile')
        best_bid = None
        best_score = -1
        for bid in bids:
            score = bid.calculate_recommendation_score()
            if score > best_score:
                best_score = score
                best_bid = bid
        return best_bid
