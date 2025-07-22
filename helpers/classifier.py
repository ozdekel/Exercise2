import re

CATEGORY_KEYWORDS = {
    "Army": ["גדוד", "military", "army", "חיל", "קרבי", "מילואים", "זום"],
    "Work": ["LinkedIn", "job", "recruitment", "career", "משרה", "עבודה", "profile", "invitation"],
    "Bills": ["invoice", "bill", "payment", "receipt", "חשבון", "חשמל", "שירות", "אישור"],
    "Personal": ["birthday", "party", "family", "יום הולדת", "משפחה"],
    "Shopping": ["order", "purchase", "cart", "עגלה", "רכישה", "הזמנה"],
    "University": ["presentation", "deck", "class", "assignment", "university", "אוניברסיטה"],
    "Entertainment": ["movie", "concert", "festival", "event", "זום", "אירוע", "invitation"],
    "Notifications": ["notification", "alert", "reminder", "התראה", "תזכורת"],
    "Promotions": ["sale", "discount", "offer", "מבצע", "הנחה", "הצעה"],
}

def categorize_email(subject: str, sender: str) -> str:
    """Categorize email based on keywords and sender rules."""
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    if "iec.co.il" in sender_lower:
        return "Bills"
    if "linkedin.com" in sender_lower:
        return "Work"
    if "@gmail.com" in sender_lower:
        return "Personal"
    if "idf.il" in sender_lower or "זום גדוד" in subject_lower:
        return "Army"

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword.lower())}\b", subject_lower):
                return category

    return "Personal"

def validate_category(category: str) -> str:
    """Ensure the category is valid and fallback if necessary."""
    if category not in CATEGORY_KEYWORDS:
        return "Personal"
    return category
