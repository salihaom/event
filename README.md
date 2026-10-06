# 🎉 EventBridge — Online Event Management System

A full-featured Django web application for managing events with manager bidding, smart bid recommendations, and trust scoring.

---

## 📦 Project Structure

```
eventmanager/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created after migrations
│
├── eventmanager/           ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/              ← Auth, roles, profiles, reviews
│   │   ├── models.py       (CustomUser, ManagerProfile, Review)
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── events/             ← Events, categories, templates
│   │   ├── models.py       (Event, Category, EventTemplate)
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py
│   │
│   ├── bidding/            ← Bids and recommendations
│   │   ├── models.py       (Bid)
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   └── notifications/      ← In-app notifications
│       ├── models.py       (Notification)
│       ├── views.py
│       ├── urls.py
│       └── admin.py
│
├── templates/
│   ├── base.html
│   ├── users/
│   ├── events/
│   ├── bidding/
│   └── notifications/
│
└── static/
    ├── css/main.css        ← Full theme with dark/light mode
    └── js/main.js          ← Theme toggle, notifications, etc.
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip

---

### Step 1 — Clone or extract the project

```bash
cd eventmanager
```

---

### Step 2 — Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Run database migrations

```bash
python manage.py makemigrations users events bidding notifications
python manage.py migrate
```

---

### Step 5 — Seed the database with sample data

```bash
python manage.py seed_data
```

This creates:
- 8 event categories (Wedding, Corporate, Birthday, etc.)
- 4 event templates (Smart Planner)
- 1 admin user
- 2 sample customers
- 3 sample managers with trust scores
- 3 sample events with bids

---

### Step 6 — Run the development server

```bash
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Role     | Username  | Password |
|----------|-----------|----------|
| Admin    | admin     | admin123 |
| Customer | customer1 | pass1234 |
| Customer | customer2 | pass1234 |
| Manager  | manager1  | pass1234 |
| Manager  | manager2  | pass1234 |
| Manager  | manager3  | pass1234 |

---

## 🗺️ URL Reference

| URL                            | Description                       |
|--------------------------------|-----------------------------------|
| `/`                            | Home page                         |
| `/users/login/`                | Login                             |
| `/users/register/customer/`    | Customer registration             |
| `/users/register/manager/`     | Manager registration              |
| `/users/dashboard/`            | Role-based dashboard redirect     |
| `/users/dashboard/customer/`   | Customer dashboard                |
| `/users/dashboard/manager/`    | Manager dashboard                 |
| `/users/dashboard/admin/`      | Admin dashboard                   |
| `/users/profile/update/`       | Manager profile update            |
| `/users/manager/<id>/`         | Manager public profile            |
| `/users/admin/users/`          | Admin: manage users               |
| `/events/create/`              | Create new event                  |
| `/events/<id>/`                | Event detail + bids               |
| `/events/my-events/`           | Customer: my events               |
| `/events/available/`           | Manager: browse events            |
| `/events/categories/`          | Admin: manage categories          |
| `/events/all/`                 | Admin: all events                 |
| `/events/budget-optimizer/`    | Budget optimizer tool             |
| `/bidding/place/<event_id>/`   | Place a bid                       |
| `/bidding/accept/<bid_id>/`    | Accept a bid                      |
| `/bidding/reject/<bid_id>/`    | Reject a bid                      |
| `/bidding/withdraw/<bid_id>/`  | Withdraw a bid                    |
| `/bidding/my-bids/`            | Manager: my bids                  |
| `/bidding/admin/all/`          | Admin: all bids                   |
| `/notifications/`              | Notifications list                |
| `/admin/`                      | Django admin panel                |

---

## ⚙️ Key Features Explained

### 🏆 Smart Bid Recommendation
Every bid gets a **recommendation score** calculated as:
```
Score = (1/price) × 0.4 + (rating/5) × 0.3 + (trust_score/100) × 0.3
```
- The highest-scoring bid is highlighted at the top as **"Best Bid"**
- A green banner with score breakdown is shown to the customer

### 🛡️ Trust Score
Manager trust is computed automatically:
```
Trust Score = (Rating × 0.5) + (Completed Events × 0.3) - (Cancellation Rate × 0.2)
```
Recalculated whenever a review is submitted or a profile is updated.

### 🔔 Notifications
- Customer is notified when a new bid arrives
- Manager is notified when their bid is accepted or rejected
- Manager is notified when a review is posted
- Badge counter updates every 30 seconds via polling

### 🌙 Dark / Light Mode
- Toggle button in the navbar
- User preference saved in `localStorage`
- All colors use CSS variables for instant theme switching

### 📋 Smart Event Planner
Event templates provide:
- Suggested services for each event category
- Estimated budget range
- Planning timeline (days needed)
Templates are shown in the sidebar on the Create Event page.

### 💡 Budget Optimizer
For any open event, shows only bids within the event budget, sorted by recommendation score. Customers can accept directly from this view.

---

## 🎨 Design System

| Token             | Light Mode   | Dark Mode    |
|-------------------|--------------|--------------|
| Background        | `#f8f7f4`    | `#111110`    |
| Card              | `#ffffff`    | `#1c1c1a`    |
| Text              | `#1a1a18`    | `#f0ede8`    |
| Accent (green)    | `#2d6a4f`    | `#52b788`    |
| Border            | `#e8e7e3`    | `#2e2e2b`    |

Fonts: **Syne** (headings) + **DM Sans** (body) — loaded from Google Fonts.

---

## 🛠️ Creating a Superuser Manually

```bash
python manage.py createsuperuser
```

Then go to `/admin/` to use the Django admin panel for direct database access.

---

## 📝 Notes

- The project uses SQLite by default — no external DB setup needed
- `DEBUG=True` is set for development; change for production
- Change `SECRET_KEY` in `settings.py` before deploying
- Static files are served by Django in development mode automatically

---

## 🔧 Common Commands

```bash
# Reset database (delete db.sqlite3, then):
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data

# Collect static files (for production):
python manage.py collectstatic

# Open Django shell:
python manage.py shell
```
