"""Mock leave data — balances, types, holidays for demo mode."""

from datetime import date

# Leave type definitions
LEAVE_TYPES = {
    "CL": {"name": "Casual Leave", "short": "CL", "max_per_year": 12, "max_consecutive": 3},
    "EL": {"name": "Earned Leave", "short": "EL", "max_per_year": 18, "max_consecutive": 15},
    "SL": {"name": "Sick Leave", "short": "SL", "max_per_year": 10, "max_consecutive": 5},
    "CO": {"name": "Comp-Off", "short": "CO", "max_per_year": 0, "max_consecutive": 2},
}

# Annual entitlement per leave type — used to seed LeaveBalance table in DB
DEFAULT_ANNUAL_ALLOCATION = {
    "CL": 12,
    "EL": 18,
    "SL": 10,
    "CO": 4,
}

# Fallback only — real balances come from the LeaveBalance table per user
DEFAULT_BALANCES = DEFAULT_ANNUAL_ALLOCATION

# 2026 public holidays (India, demo set)
PUBLIC_HOLIDAYS = [
    date(2026, 1, 26),   # Republic Day
    date(2026, 3, 25),   # Holi
    date(2026, 4, 10),   # Good Friday
    date(2026, 4, 14),   # Dr. Ambedkar Jayanti
    date(2026, 5, 1),    # Labour Day
    date(2026, 8, 15),   # Independence Day
    date(2026, 10, 2),   # Gandhi Jayanti
    date(2026, 10, 20),  # Dussehra
    date(2026, 11, 4),   # Diwali
    date(2026, 11, 5),   # Diwali (2nd day)
    date(2026, 12, 25),  # Christmas
]

HOLIDAY_NAMES = {
    date(2026, 1, 26): "Republic Day",
    date(2026, 3, 25): "Holi",
    date(2026, 4, 10): "Good Friday",
    date(2026, 4, 14): "Dr. Ambedkar Jayanti",
    date(2026, 5, 1):  "Labour Day",
    date(2026, 8, 15): "Independence Day",
    date(2026, 10, 2): "Gandhi Jayanti",
    date(2026, 10, 20): "Dussehra",
    date(2026, 11, 4): "Diwali",
    date(2026, 11, 5): "Diwali (2nd day)",
    date(2026, 12, 25): "Christmas",
}

# Leave type aliases for NLP normalization
LEAVE_TYPE_ALIASES = {
    "casual": "CL", "casual leave": "CL", "cl": "CL",
    "earned": "EL", "earned leave": "EL", "el": "EL", "privilege": "EL", "pl": "EL",
    "sick": "SL", "sick leave": "SL", "sl": "SL", "medical": "SL",
    "comp": "CO", "comp off": "CO", "comp-off": "CO", "compensatory": "CO", "co": "CO",
}

# Status labels
STATUS_LABELS = {
    "pending": "Pending Approval",
    "approved": "Approved",
    "rejected": "Rejected",
    "cancelled": "Cancelled",
}
