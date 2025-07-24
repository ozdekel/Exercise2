# Gmail AI Helper

An AI-powered tool that classifies your last 10 Gmail emails into categories using a local LLM and caches the results in Redis. This project is designed to demonstrate technical maturity through clean code, good testing practices, and local inference.

## 🔧 Features

- Authenticate with Gmail via OAuth
- Fetch the 10 most recent emails
- Classify emails into categories using GPT4All
- Cache responses in Redis to reduce redundant inference
- Display category distribution using a pie chart

## 📁 Project Structure
Exercise2/
├── main.py
├── requirements.txt
├── README.md
│
├── helpers/
│   ├── auth.py
│   ├── cache.py
│   ├── classifier.py
│   ├── llm_interface.py
│   └── visualizer.py
│
└── tests/
    ├── test_auth.py
    ├── test_cache.py
    ├── test_classifier.py
    ├── test_llm_interface.py
    └── test_main.py

