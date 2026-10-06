/* EventBridge — Main JavaScript */

// ============ DARK MODE TOGGLE ============
const THEME_KEY = 'eventbridge_theme';

function getTheme() {
  return localStorage.getItem(THEME_KEY) || 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = getTheme();
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// Apply theme immediately on load
document.addEventListener('DOMContentLoaded', function () {
  applyTheme(getTheme());

  // Theme toggle button
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // Mobile hamburger
  const hamburger = document.getElementById('navHamburger');
  const mobileNav = document.getElementById('navMobile');
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      mobileNav.classList.toggle('open');
      hamburger.textContent = mobileNav.classList.contains('open') ? '✕' : '☰';
    });
  }

  // Auto-dismiss alerts after 5s
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      if (alert.parentNode) {
        alert.style.transition = 'opacity 0.4s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 400);
      }
    }, 5000);
  });

  // Notification badge polling
  pollNotifications();
  setInterval(pollNotifications, 30000);
});

// ============ NOTIFICATION POLLING ============
function pollNotifications() {
  const badge = document.getElementById('notif-badge');
  if (!badge) return;

  fetch('/notifications/unread-count/')
    .then(r => r.json())
    .then(data => {
      if (data.count > 0) {
        badge.textContent = data.count;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    })
    .catch(() => {});
}

// ============ SCORE BAR ANIMATION ============
document.addEventListener('DOMContentLoaded', function () {
  // Animate score bars on load
  const bars = document.querySelectorAll('.score-bar-fill');
  bars.forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => {
      bar.style.transition = 'width 0.8s ease';
      bar.style.width = target;
    }, 100);
  });
});

// ============ FORM VALIDATION HELPERS ============
document.addEventListener('DOMContentLoaded', function () {
  // Budget vs price warning on bid form
  const priceInput = document.querySelector('input[name="price"]');
  const budgetVal = priceInput && priceInput.getAttribute('max');

  if (priceInput && budgetVal) {
    const hint = priceInput.closest('.form-group').querySelector('.form-hint');

    priceInput.addEventListener('input', function () {
      const val = parseFloat(this.value);
      const budget = parseFloat(budgetVal);
      if (hint) {
        if (val > budget) {
          hint.style.color = 'var(--danger)';
          hint.textContent = `⚠️ Your bid (₹${val.toLocaleString()}) exceeds the event budget (₹${budget.toLocaleString()}). Customers may prefer bids within budget.`;
        } else if (val > 0) {
          const savings = budget - val;
          hint.style.color = 'var(--success)';
          hint.textContent = `✓ Within budget. Saves customer ₹${savings.toLocaleString()} vs. full budget.`;
        } else {
          hint.style.color = 'var(--text-muted)';
          hint.textContent = `Event budget: ₹${budget.toLocaleString()}. Competitive bids get better recommendation scores.`;
        }
      }
    });
  }
});

// ============ CONFIRM DIALOGS HANDLED IN HTML ============
// All confirm() calls are inline onclick handlers in templates

// ============ ACCESSIBILITY: CLOSE MODALS ON ESC ============
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    // close any open mobile nav
    const mobileNav = document.getElementById('navMobile');
    if (mobileNav && mobileNav.classList.contains('open')) {
      mobileNav.classList.remove('open');
      const hamburger = document.getElementById('navHamburger');
      if (hamburger) hamburger.textContent = '☰';
    }
  }
});
