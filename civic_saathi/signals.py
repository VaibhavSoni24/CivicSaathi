"""
Django signals for CivicSaathi.

Email notifications are handled explicitly in views_api.py and management
commands (auto_escalate.py) to avoid duplicate emails. No email logic lives
here intentionally.
"""
