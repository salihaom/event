from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('manager', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)

    def is_customer(self):
        return self.role == 'customer'

    def is_manager(self):
        return self.role == 'manager'

    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff

    def __str__(self):
        return f"{self.username} ({self.role})"


class ManagerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='manager_profile'
    )
    bio = models.TextField(blank=True)
    services_offered = models.TextField(help_text="Comma-separated list of services")
    price_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField(default=0)
    completed_events = models.PositiveIntegerField(default=0)
    cancelled_events = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_trust_score(self):
        """Trust Score = (Rating x 0.5) + (Completed x 0.3) - (CancellationRate x 0.2)"""
        total = self.completed_events + self.cancelled_events
        cancellation_rate = (self.cancelled_events / total * 100) if total > 0 else 0
        completed_factor = min(self.completed_events * 0.3, 30)
        score = float(self.average_rating) * 0.5 + completed_factor - cancellation_rate * 0.2
        self.trust_score = max(0, round(score, 2))
        self.save(update_fields=['trust_score'])
        return self.trust_score

    def get_services_list(self):
        return [s.strip() for s in self.services_offered.split(',') if s.strip()]

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Review(models.Model):
    reviewer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='given_reviews'
    )
    manager = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_reviews'
    )
    # String reference to avoid circular import with events app
    event = models.ForeignKey(
        'events.Event', on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'event')

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.manager.username}"
