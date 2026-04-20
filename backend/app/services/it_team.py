"""IT team configuration — members, category assignments, and SLA constants."""

# SLA resolution targets by priority (in hours)
SLA_HOURS = {
    "P1": 24,    # 1 day  — Critical / outage
    "P2": 48,    # 2 days — High impact
    "P3": 168,   # 7 days — Normal
    "P4": 336,   # 14 days — Low
}

# Demo IT team members seeded on startup
IT_TEAM_MEMBERS = [
    {
        "email": "it.manager@impetus.com",
        "full_name": "Rajesh Kumar",
        "employee_id": "EMP-IT-001",
        "department": "IT",
        "role": "it_agent",
        "password": "ChangeMe123!",
    },
    {
        "email": "it.network@impetus.com",
        "full_name": "Priya Sharma",
        "employee_id": "EMP-IT-002",
        "department": "IT",
        "role": "it_agent",
        "password": "ChangeMe123!",
    },
    {
        "email": "it.hardware@impetus.com",
        "full_name": "Arjun Mehta",
        "employee_id": "EMP-IT-003",
        "department": "IT",
        "role": "it_agent",
        "password": "ChangeMe123!",
    },
    {
        "email": "it.security@impetus.com",
        "full_name": "Kavitha Nair",
        "employee_id": "EMP-IT-004",
        "department": "IT",
        "role": "it_agent",
        "password": "ChangeMe123!",
    },
]

# Ticket category → responsible IT agent email
CATEGORY_ASSIGNMENT = {
    "Network": "it.network@impetus.com",
    "Hardware": "it.hardware@impetus.com",
    "Software": "it.hardware@impetus.com",
    "Access": "it.security@impetus.com",
    "Security": "it.security@impetus.com",
    "General": "it.network@impetus.com",
}

# Reporting manager relationships: email → manager email
MANAGER_MAP = {
    "it.network@impetus.com": "it.manager@impetus.com",
    "it.hardware@impetus.com": "it.manager@impetus.com",
    "it.security@impetus.com": "it.manager@impetus.com",
    "it.manager@impetus.com": None,
}

# Job title by email
TITLE_MAP = {
    "it.manager@impetus.com": "IT Manager",
    "it.network@impetus.com": "Network Specialist",
    "it.hardware@impetus.com": "Hardware & Software Specialist",
    "it.security@impetus.com": "Security & Access Specialist",
}
