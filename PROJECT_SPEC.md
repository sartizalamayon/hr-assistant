# HR Assistant — Project Specification

## 1. Overview

HR Assistant is a simple internal web app that lets HR upload company policy
PDFs and lets employees ask natural-language questions about those policies.
The app searches the uploaded documents (RAG) to answer questions grounded in
actual policy text. When it can't find a confident answer, it logs the
question to an "Unanswered Questions" queue that HR can review and answer
later.

## 2. Goals / Non-Goals

**Goals**
- Let HR upload/manage PDF policy documents.
- Let employees ask questions in plain language and get answers sourced from
  those documents.
- Never fabricate answers — if the retrieved context doesn't support a
  confident answer, save the question for HR instead of guessing.
- Give HR a simple dashboard to review unanswered questions and mark them
  resolved (optionally feeding the answer back into the knowledge base).

**Non-Goals (MVP)**
- No real SSO/OAuth integration (dummy button only — see §5).
- No legal/compliance advice generation — answers are informational, sourced
  strictly from uploaded documents.
- No multi-tenant support (single company/instance).
- No mobile app — responsive web only.
- No document editing/annotation inside the app; PDFs are uploaded as-is.

## 3. Users & Roles

Two roles, both authenticated through the same login page but routed to
different portals:

| Role | Capabilities |
|---|---|
| **Employee** | Ask questions, view their own question/answer history |
| **HR** | Everything an employee can do, plus: upload/delete policy PDFs, view the Unanswered Questions queue, answer/resolve questions |

## 4. Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: Server-rendered HTML (Jinja2 templates) + CSS + vanilla JS for
  interactivity (async question submission, upload progress, etc.). No SPA
  framework — kept simple per requirements.
- **Database**: PostgreSQL with the `pgvector` extension (single database for
  both relational data and embedding vectors).
- **LLM (answer generation)**: Groq API (e.g. Llama 3.x / Mixtral models
  hosted on Groq) — used only for generating the final answer from retrieved
  context, and for a lightweight yes/no "can this be answered from context?"
  confidence check.
- **Embeddings (retrieval)**: A local open-source sentence-embedding model
  (e.g. `sentence-transformers/all-MiniLM-L6-v2`) run in-process. Groq has no
  embeddings endpoint, so this keeps retrieval free of an extra external
  dependency. *(Swappable later for a hosted embeddings API if preferred.)*
- **PDF parsing**: `pypdf` or `pdfplumber` for text extraction.
- **Auth**: Simple session-based auth (email + password, hashed with
  `bcrypt`/`passlib`), two login entry points (Employee / HR), plus a
  non-functional "Sign in with Google" button shown for visual/demo purposes
  only.

## 5. Authentication Flow

- Single login page (`/login`) with:
  - **"Employee Login"** button/tab → email + password form → on success,
    redirect to `/employee` (chat/ask UI).
  - **"HR Login"** button/tab → email + password form → on success, redirect
    to `/hr` (dashboard).
  - **"Sign in with Google"** button — dummy/placeholder. Clicking it shows a
    disabled/mock state (e.g. "SSO coming soon") and does not perform real
    OAuth. Wired up for future real SSO integration.
- Sessions stored via signed cookies (FastAPI `SessionMiddleware` or a JWT in
  an httpOnly cookie).
- Passwords hashed at rest; no plaintext storage.
- Role is stored on the `users` table and enforced server-side on every
  protected route (an Employee cannot hit HR-only endpoints, and vice versa).

## 6. Core Features

### 6.1 HR: Document Management
- Upload one or more PDF files (drag-and-drop or file picker).
- On upload: extract text, chunk it, generate embeddings, store chunks +
  vectors in Postgres linked to the source document.
- List uploaded documents with filename, upload date, uploader, chunk count.
- Delete a document (cascades: removes its chunks/embeddings).

### 6.2 Employee: Ask a Question
- Simple chat-style input box: employee types a question.
- Backend retrieves the top-N most relevant chunks via pgvector similarity
  search, then calls Groq with the question + retrieved context to generate
  an answer.
- If the model's confidence/groundedness check fails (context doesn't
  actually support an answer, or similarity scores are below a threshold),
  the app does **not** show a fabricated answer. Instead it:
  - Tells the employee the question has been forwarded to HR.
  - Saves the question (with employee id, timestamp, question text) to the
    `unanswered_questions` table with status `pending`.
- Employee can view their own question history and see status
  (`answered` inline vs `pending with HR` vs `resolved by HR`).

### 6.3 HR: Unanswered Questions Queue
- Dashboard list of all pending questions, newest first, with asker (or
  anonymized, see open question in §9) and timestamp.
- HR can type an answer and mark it `resolved` — the answer is shown back to
  the employee (e.g. in their history, or via a notification-style flag).
- Optional (nice-to-have, not required for MVP): "Add to knowledge base"
  action that turns the HR-authored answer into a new indexed chunk so future
  similar questions can be auto-answered.

## 7. Data Model (draft)

```
users
  id, email, password_hash, role (employee|hr), created_at

documents
  id, filename, uploaded_by (fk users), uploaded_at, storage_path

document_chunks
  id, document_id (fk documents), chunk_text, embedding (vector), chunk_index

questions
  id, asked_by (fk users), question_text, asked_at,
  status (answered_by_ai|pending|resolved_by_hr),
  ai_answer (nullable), hr_answer (nullable),
  resolved_by (fk users, nullable), resolved_at (nullable)
```

## 8. API Endpoints (draft)

| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/auth/login/employee` | public | Employee login |
| POST | `/auth/login/hr` | public | HR login |
| POST | `/auth/logout` | any | Logout |
| POST | `/hr/documents` | HR | Upload PDF |
| GET | `/hr/documents` | HR | List documents |
| DELETE | `/hr/documents/{id}` | HR | Delete document |
| POST | `/questions` | Employee | Submit a question, get AI answer or pending status |
| GET | `/questions/mine` | Employee | View own question history |
| GET | `/hr/questions/pending` | HR | List unanswered questions |
| POST | `/hr/questions/{id}/resolve` | HR | Submit HR answer, mark resolved |

## 9. Open Questions / Assumptions to confirm

1. **Anonymity**: Should employee identity be visible to HR on questions, or
   anonymized? (Assumed: visible, since HR may need to follow up.)
2. **Confidence threshold**: What similarity/confidence cutoff decides
   "answer directly" vs "escalate to HR"? (Will start with a tunable
   threshold + a secondary LLM groundedness check, adjustable later.)
3. **Notifications**: When HR resolves a question, does the employee need an
   email/notification, or is checking their history in-app enough? (Assumed:
   in-app only for MVP.)
4. **Document versioning**: If HR re-uploads an updated policy, should the
   old version be replaced or kept as history? (Assumed: replaced/deleted
   manually by HR for MVP — no automatic versioning.)
5. **Embeddings model**: Confirm the local `sentence-transformers` approach
   is acceptable, vs. wiring a hosted embeddings API instead.

## 10. Non-Functional Requirements

- Runs locally via `uvicorn` + Docker Compose (app + Postgres).
- No PII beyond email/password/role stored for auth.
- PDF uploads size-limited (e.g. 20MB) and validated as PDF mime-type.
- Basic rate limiting on the question endpoint to avoid Groq API abuse.
