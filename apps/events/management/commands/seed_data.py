"""
Management command to seed the database with initial data.
Run: python manage.py seed_data
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.events.models import Category, EventTemplate, Event
from apps.users.models import ManagerProfile
from apps.bidding.models import Bid

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🌱 Seeding database...'))

        # ── Categories ───────────────────────────────────────────
        categories_data = [
            ('Wedding', '💍', 'Full wedding planning and coordination services'),
            ('Corporate Event', '🏢', 'Corporate meetings, conferences, and team events'),
            ('Birthday Party', '🎂', 'Birthday celebrations for all ages'),
            ('Concert & Music', '🎵', 'Live music events, concerts, and festivals'),
            ('Conference', '🎤', 'Professional conferences and seminars'),
            ('Exhibition', '🖼️', 'Art exhibitions, trade shows, and expos'),
            ('Sports Event', '⚽', 'Sporting events and tournaments'),
            ('Cultural Festival', '🎭', 'Cultural celebrations and festivals'),
        ]
        categories = {}
        for name, icon, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'description': desc}
            )
            categories[name] = cat
            if created:
                self.stdout.write(f'  ✓ Category: {name}')

        # ── Event Templates ───────────────────────────────────────
        templates_data = [
            {
                'category': 'Wedding',
                'name': 'Classic Wedding Package',
                'description': 'A full-service wedding with venue, catering, decoration, photography, and entertainment for up to 200 guests.',
                'suggested_services': '["Catering", "Photography", "Videography", "Decoration", "Sound & Lighting", "MC/Host"]',
                'timeline_days': 90,
                'budget_min': 300000,
                'budget_max': 800000,
            },
            {
                'category': 'Corporate Event',
                'name': 'Annual Company Gala',
                'description': 'A formal corporate gala with dinner, awards ceremony, entertainment, and team activities.',
                'suggested_services': '["Catering", "AV Equipment", "Stage Setup", "Photography", "Event Coordination"]',
                'timeline_days': 45,
                'budget_min': 150000,
                'budget_max': 500000,
            },
            {
                'category': 'Birthday Party',
                'name': 'Grand Birthday Celebration',
                'description': 'A memorable birthday party with themed decoration, catering, entertainment, and photography.',
                'suggested_services': '["Catering", "Decoration", "Photography", "Entertainment", "Cake"]',
                'timeline_days': 14,
                'budget_min': 20000,
                'budget_max': 80000,
            },
            {
                'category': 'Conference',
                'name': 'Professional Conference',
                'description': 'A 1-2 day professional conference with multiple tracks, keynote speakers, and networking sessions.',
                'suggested_services': '["Venue", "AV Equipment", "Catering", "Photography", "Event Management"]',
                'timeline_days': 60,
                'budget_min': 100000,
                'budget_max': 400000,
            },
        ]
        for t in templates_data:
            cat = categories.get(t['category'])
            if cat:
                tmpl, created = EventTemplate.objects.get_or_create(
                    name=t['name'],
                    defaults={
                        'category': cat,
                        'description': t['description'],
                        'suggested_services': t['suggested_services'],
                        'timeline_days': t['timeline_days'],
                        'estimated_budget_min': t['budget_min'],
                        'estimated_budget_max': t['budget_max'],
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Template: {t["name"]}')

        # ── Admin User ────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@eventbridge.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
            )
            self.stdout.write('  ✓ Admin user: admin / admin123')

        # ── Sample Customers ──────────────────────────────────────
        customers_data = [
            ('customer1', 'Priya', 'Sharma', 'priya@example.com', 'Mumbai'),
            ('customer2', 'Rahul', 'Gupta', 'rahul@example.com', 'Delhi'),
        ]
        customers = {}
        for uname, fname, lname, email, city in customers_data:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(
                    username=uname, email=email, password='pass1234',
                    first_name=fname, last_name=lname,
                    role='customer', city=city,
                )
                customers[uname] = u
                self.stdout.write(f'  ✓ Customer: {uname} / pass1234')
            else:
                customers[uname] = User.objects.get(username=uname)

        # ── Sample Managers ───────────────────────────────────────
        managers_data = [
            {
                'username': 'manager1',
                'first_name': 'Arjun', 'last_name': 'Mehta',
                'email': 'arjun@example.com',
                'city': 'Mumbai',
                'services': 'Catering, Decoration, Photography, Sound & Lighting',
                'price_min': 50000, 'price_max': 500000,
                'location': 'Mumbai',
                'experience': 8,
                'bio': 'Expert event manager with 8 years of experience in weddings and corporate events.',
                'completed': 45, 'cancelled': 2, 'rating': 4.7,
            },
            {
                'username': 'manager2',
                'first_name': 'Sneha', 'last_name': 'Patel',
                'email': 'sneha@example.com',
                'city': 'Bangalore',
                'services': 'Event Coordination, AV Equipment, Photography, Videography',
                'price_min': 30000, 'price_max': 300000,
                'location': 'Bangalore',
                'experience': 5,
                'bio': 'Specializing in corporate events and conferences with state-of-the-art AV solutions.',
                'completed': 28, 'cancelled': 1, 'rating': 4.5,
            },
            {
                'username': 'manager3',
                'first_name': 'Vikram', 'last_name': 'Singh',
                'email': 'vikram@example.com',
                'city': 'Delhi',
                'services': 'Catering, Decoration, Entertainment, MC/Host',
                'price_min': 20000, 'price_max': 200000,
                'location': 'Delhi',
                'experience': 3,
                'bio': 'Young and dynamic event planner known for creative, budget-friendly solutions.',
                'completed': 15, 'cancelled': 3, 'rating': 4.2,
            },
        ]
        managers = {}
        for m in managers_data:
            if not User.objects.filter(username=m['username']).exists():
                u = User.objects.create_user(
                    username=m['username'], email=m['email'], password='pass1234',
                    first_name=m['first_name'], last_name=m['last_name'],
                    role='manager', city=m['city'],
                )
                profile = ManagerProfile.objects.create(
                    user=u,
                    bio=m['bio'],
                    services_offered=m['services'],
                    price_min=m['price_min'],
                    price_max=m['price_max'],
                    location=m['location'],
                    experience_years=m['experience'],
                    completed_events=m['completed'],
                    cancelled_events=m['cancelled'],
                    average_rating=m['rating'],
                )
                profile.calculate_trust_score()
                managers[m['username']] = u
                self.stdout.write(f'  ✓ Manager: {m["username"]} / pass1234')
            else:
                managers[m['username']] = User.objects.get(username=m['username'])

        # ── Sample Events ─────────────────────────────────────────
        c1 = customers.get('customer1') or User.objects.filter(role='customer').first()
        c2 = customers.get('customer2') or c1

        if c1 and Event.objects.count() == 0:
            events_data = [
                {
                    'organizer': c1,
                    'title': 'Annual Tech Summit 2025',
                    'description': 'A 2-day technology conference for 300 attendees with keynote speakers, workshops, and networking sessions. Requires full AV setup, catering, and event coordination.',
                    'category': categories.get('Conference'),
                    'budget': 350000,
                    'location': 'Mumbai',
                    'event_date': '2025-09-15',
                    'status': 'open',
                },
                {
                    'organizer': c1,
                    'title': 'Silver Jubilee Wedding Reception',
                    'description': 'An elegant wedding reception for 250 guests requiring floral decoration, 5-course dinner catering, professional photography/videography, and live music entertainment.',
                    'category': categories.get('Wedding'),
                    'budget': 600000,
                    'location': 'Mumbai',
                    'event_date': '2025-11-20',
                    'status': 'open',
                },
                {
                    'organizer': c2,
                    'title': 'Rohan\'s 30th Birthday Bash',
                    'description': 'A grand 30th birthday party for 80 guests with Bollywood theme, DJ, catering, and photo booth.',
                    'category': categories.get('Birthday Party'),
                    'budget': 60000,
                    'location': 'Delhi',
                    'event_date': '2025-08-10',
                    'status': 'open',
                },
            ]
            for ed in events_data:
                event = Event.objects.create(**ed)
                self.stdout.write(f'  ✓ Event: {event.title}')

                # Add sample bids to first event
                if ed['title'] == 'Annual Tech Summit 2025':
                    for uname, price, proposal in [
                        ('manager1', 320000, 'Our team has organized 10+ tech summits. We provide full AV setup with 4K projectors, professional catering with live counters, and a dedicated 5-person event team.'),
                        ('manager2', 280000, 'Specializing in corporate events with cutting-edge AV solutions. Package includes high-speed WiFi, live streaming, catering for 300, and post-event photo book.'),
                        ('manager3', 220000, 'Budget-friendly but high-quality. Includes all AV equipment, vegetarian catering, and a professional MC for both days.'),
                    ]:
                        mgr = managers.get(uname)
                        if mgr:
                            bid = Bid.objects.create(
                                event=event,
                                manager=mgr,
                                price=price,
                                proposal=proposal,
                                status='pending'
                            )
                            bid.calculate_recommendation_score()
                            self.stdout.write(f'    ↳ Bid by {uname}: ₹{price:,}')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!\n'))
        self.stdout.write('─' * 50)
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:     admin      / admin123')
        self.stdout.write('  Customer:  customer1  / pass1234')
        self.stdout.write('  Customer:  customer2  / pass1234')
        self.stdout.write('  Manager:   manager1   / pass1234')
        self.stdout.write('  Manager:   manager2   / pass1234')
        self.stdout.write('  Manager:   manager3   / pass1234')
        self.stdout.write('─' * 50)
