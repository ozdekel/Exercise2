# Gmail AI Helper

Classify your recent Gmail emails into categories using OpenAI embeddings, cache them in Redis, and visualize the results in a pie chart.

---

## Overview

Gmail AI Helper retrieves your ten most recent emails (subject + sender), assigns each to a category such as **Work**, **Personal** or **Promotions**, stores the results for quick repeat runs, and displays a clear chart of the breakdown. All processing happens on your machine—no email data ever leaves your device.

---

## Key Advantages
- **🔒 Privacy‑Focused**  
  All email content is processed locally (Redis + local cache). No emails are sent or stored externally.

- **🧠 Smart Classification**  
  Combines OpenAI embeddings with keyword rules to maximize accuracy and fallback reliability.

- **⚡ Blazing Fast**  
  Uses Redis to cache emails and embeddings — avoids redundant API calls and speeds up repeated runs.

- **📊 Visual Insights**  
  Instantly generates a pie chart showing the distribution of your email categories.

- **🧪 Fully Tested**  
  Includes unit tests for every component and integration test for full pipeline verification.

- **🔌 Plug-and-Play**  
  Easy setup using `.env` or environment variables. Works out of the box after Gmail auth.

---

## 🛠 Technologies Used

<div align="center">

| Category        | Technology                             |
|----------------|-----------------------------------------|
| Programming     | Python 3.10+                           |
| APIs            | OpenAI API (embeddings + GPT models)  |
| Email Access    | Gmail API via Google OAuth             |
| Caching         | Redis                                  |
| Data Format     | JSON, Pickle                           |
| Visualization   | Matplotlib (pie chart)                 |
| Environment     | Python-dotenv (.env config)            |
| Testing         | Pytest                                 |

</div>

---

## Installation

1. Clone the repositoy :
```bash
git clone https://github.com/your‑handle/gmail‑ai‑helper.git
cd gmail‑ai‑helper
```
2. Activate the venv : 
```bash
python -m venv .venv && source .venv/bin/activate
```
3. Install dependencies :
```bash 
pip install -r requirements.txt
```

---

## Configuration

Create a Google Cloud OAuth 2.0 Client (Desktop) and download credentials.json.

Export or place environment variables (or a .env file):

```bash
export GOOGLE_CREDENTIALS_PATH="/abs/path/credentials.json"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export MODEL_PATH="/abs/path/Phi-3-mini-4k-instruct.Q4_0.gguf"
```

First run will launch a browser window for Gmail consent; a token.json will be stored locally for future runs.

---

## Usage

```bash
python main.py
```

CLI steps:
- Authenticate (or refresh) Gmail token
- Fetch last 10 emails 
- Classify via GPT4All (cached when possible) 
- Print results and open pie‑chart window

---

## Testing

```bash
pytest -s
Unit tests cover every helper module plus a mocked integration test for the full pipeline.
```

---

# Contributing

Fork ➜ create feature branch

Write code and tests

Submit pull request explaining the change

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.