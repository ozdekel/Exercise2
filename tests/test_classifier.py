import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from helpers.classifier import categorize_email, validate_category

@pytest.mark.parametrize("subject,sender,expected", [
    ("Invoice from IEC", "support@iec.co.il", "Bills"),
    ("You've got a new connection", "noreply@linkedin.com", "Work"),
    ("Birthday party invite", "friend@gmail.com", "Personal"),
    ("זימון מילואים", "unit@idf.il", "Army"),
    ("Upcoming assignment due", "teacher@university.edu", "University"),
    ("🎉 Huge Sale now!", "sales@shop.com", "Promotions"),
    ("Concert Tickets", "ticket@events.com", "Entertainment"),
    ("Reminder: update your password", "alert@security.com", "Notifications"),
    ("Order confirmed", "amazon@store.com", "Shopping"),
    ("Random subject", "unknown@domain.com", "Personal"),
])
def test_categorize_email(subject, sender, expected):
    assert categorize_email(subject, sender) == expected

@pytest.mark.parametrize("input_category,expected", [
    ("Work", "Work"),
    ("Army", "Army"),
    ("NonExistentCategory", "Personal"),
    ("", "Personal"),
])
def test_validate_category(input_category, expected):
    assert validate_category(input_category) == expected
