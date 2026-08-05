# HR Assistant

## Running it

```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Then open http://127.0.0.1:8000 in your browser. Press `Ctrl+C` in the terminal to stop it.

## Test accounts

| Role | Email | Password |
|---|---|---|
| Employee | employee@example.com | employeepassword123 |
| HR | hr@example.com | hrpassword123 |

Create more accounts with `python -m scripts.seed_users` (edit the list in that file first).

## One-time setup (already done)

- `python -m scripts.init_db` — creates the `hr_assist` Postgres database and tables
- `.env` — holds your Groq and Cohere API keys (never commit this file)

## What it does

- HR logs in, uploads policy PDFs, and reviews/answers questions the AI couldn't handle.
- Employees log in and ask questions in a chat interface. Answers are generated only from
  the uploaded policy text (with a source citation) — if nothing relevant is found, the
  question is forwarded to HR instead of guessing.
