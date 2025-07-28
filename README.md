# Gmail AI Helper

Classify your recent Gmail emails into categories using OpenAI embeddings, cache them in Redis, and visualize the results in a pie chart.

---

## Overview

Gmail AI Helper retrieves your ten most recent emails (subject + sender), assigns each to a category such as **Work**, **Personal** or **Promotions**, stores the results for quick repeat runs, and displays a clear chart of the breakdown. All processing happens on your machine—no email data ever leaves your device.

---

## Key Advantages
- **Local‑only AI** – GPT4All runs entirely on‑device, so your email content remains private.  
- **Redis caching** – Avoids repeated LLM calls for the same messages, speeding up future executions.  
- **Clean CLI experience** – One command fetches, classifies, and plots.  
- **Modular architecture** – Each concern (auth, cache, LLM, visuals) lives in its own helper module.  
- **Full test suite** – Pytest covers every helper plus an end‑to‑end run.

---

## Technologies Used
| Purpose            | Library / Tool                       |
|--------------------|--------------------------------------|
| Gmail API access   | `google-api-python-client`, `google-auth-oauthlib` |
| Local LLM          | `gpt4all`                            |
| Caching            | `redis` (via `redis-py`)             |
| Charts             | `matplotlib`                         |
| Testing            | `pytest`                             |

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