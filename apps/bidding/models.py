from django.db import models
from django.conf import settings


class Bid(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='bids'
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='placed_bids'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recommendation_score = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'manager')
        ordering = ['-recommendation_score', 'price']

    def __str__(self):
        return f"Bid by {self.manager.username} for {self.event.title}"

    def calculate_recommendation_score(self):
        try:
            profile = self.manager.manager_profile
            price = float(self.price) if float(self.price) > 0 else 1.0
            rating = float(profile.average_rating)
            trust = float(profile.trust_score)
            score = (1.0 / price) * 0.4 + (rating / 5.0) * 0.3 + (trust / 100.0) * 0.3
            self.recommendation_score = round(score, 4)
            self.save(update_fields=['recommendation_score'])
            return float(self.recommendation_score)
        except Exception:
            return 0.0
