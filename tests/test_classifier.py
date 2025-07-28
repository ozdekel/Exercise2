import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pickle
from helpers.classifier import (
    keyword_based_category as categorize_email,
    validate_category,
    embedding_based_category as classify_with_embedding
)
import helpers.classifier as classifier_module


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


def test_classify_with_embedding(monkeypatch):
    # Dummy embeddings to simulate the email_embeddings.pkl content
    dummy_embeddings = [
        {
            "embedding": [0.1] * 1536,
            "category": "Work",
            "text": "from1 subject1"
        },
        {
            "embedding": [0.9] * 1536,
            "category": "Bills",
            "text": "from2 subject2"
        }
    ]

    # Fake response to simulate OpenAI embedding API
    class DummyResponse:
        def __init__(self):
            self.data = [type("obj", (object,), {"embedding": [0.96] * 1536})()]

    class DummyEmbeddings:
        def create(self, model, input):
            return DummyResponse()

    class DummyClient:
        embeddings = DummyEmbeddings()

    # Patch openai_client and load_embeddings
    monkeypatch.setattr(classifier_module, "openai_client", DummyClient())
    monkeypatch.setattr(classifier_module, "load_embeddings", lambda: dummy_embeddings)

    subject = "חשבונית תשלום עבור ביטוח רכב"
    sender = "billing@insurance.co.il"
    result = classify_with_embedding(subject, sender)

    assert result == "Bills"
