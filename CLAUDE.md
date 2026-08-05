# CLAUDE.md

Guidance for Claude Code when working in this repository.

See [PROJECT_SPEC.md](PROJECT_SPEC.md) for the full product/technical spec.

## Project Summary

HR Assistant: employees ask questions about HR policy PDFs that HR uploads.
Answers are generated via RAG (Postgres/pgvector retrieval + Groq for
generation). Unanswerable questions are logged for HR to review.

## About Me
I am a non-technical person. Explain technical concepts in simple language before making important decisions. If there are multiple options, briefly explain the pros and cons and recommend the one you think is best.


## Rules
- Keep the project as simple as possible.
- Prioritize clean code over clever solutions.
- Don't make assumptions—ask questions when requirements are unclear.
- Prefer free whenever possible.