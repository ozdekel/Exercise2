import matplotlib.pyplot as plt

def plot_email_categories(categories_count: dict) -> None:
    """Plot a pie chart of email categories."""
    labels = list(categories_count.keys())
    sizes = list(categories_count.values())

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Email Categories Distribution")
    plt.show(block=True)
