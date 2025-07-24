import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from helpers.visualizer import plot_email_categories

@patch("helpers.visualizer.plt.show")
@patch("helpers.visualizer.plt.pie")
@patch("helpers.visualizer.plt.figure")
@patch("helpers.visualizer.plt.title")
def test_plot_email_categories(mock_title, mock_figure, mock_pie, mock_show):
    data = {
        "Work": 10,
        "Personal": 5,
        "Promotions": 3
    }

    plot_email_categories(data)

    mock_figure.assert_called_once_with(figsize=(8, 6))
    mock_pie.assert_called_once()
    mock_title.assert_called_once_with("Email Categories Distribution")
    mock_show.assert_called_once_with(block=True)
