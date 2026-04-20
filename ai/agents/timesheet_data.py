"""Mock timesheet data — project codes, activities for demo mode."""

# Active project codes (in real mode, fetched from HRMS/Jira)
MOCK_PROJECTS = [
    {"code": "IMPETUS-INT", "name": "Internal / Admin", "billable": False},
    {"code": "IMPETUS-AI",  "name": "ImpetusAI Platform", "billable": True},
    {"code": "PROJ-NMG",    "name": "NMG Network Intelligence", "billable": True},
    {"code": "PROJ-FINAI",  "name": "FinAI Payroll Automation", "billable": True},
    {"code": "PROJ-CLOUD",  "name": "Cloud Migration", "billable": True},
    {"code": "TRAINING",    "name": "Training & Learning", "billable": False},
    {"code": "LEAVE",       "name": "Leave (auto)", "billable": False},
]

PROJECT_CODE_MAP = {p["code"]: p for p in MOCK_PROJECTS}
PROJECT_NAME_MAP = {p["name"].lower(): p["code"] for p in MOCK_PROJECTS}

# Standard activity types
ACTIVITY_TYPES = [
    "Development",
    "Code Review",
    "Testing / QA",
    "Design",
    "Meeting",
    "Documentation",
    "DevOps / Infra",
    "Client Call",
    "Training",
    "Support",
    "Planning",
    "Other",
]

# Activity aliases for NLP
ACTIVITY_ALIASES = {
    "dev": "Development",
    "coding": "Development",
    "code": "Development",
    "review": "Code Review",
    "pr": "Code Review",
    "test": "Testing / QA",
    "qa": "Testing / QA",
    "design": "Design",
    "meeting": "Meeting",
    "call": "Client Call",
    "client": "Client Call",
    "docs": "Documentation",
    "documentation": "Documentation",
    "infra": "DevOps / Infra",
    "devops": "DevOps / Infra",
    "deploy": "DevOps / Infra",
    "training": "Training",
    "support": "Support",
    "planning": "Planning",
    "standup": "Meeting",
    "scrum": "Meeting",
}

# Validation rules
MAX_HOURS_PER_DAY = 12
MIN_HOURS_PER_ENTRY = 0.5
STANDARD_HOURS_PER_WEEK = 40
