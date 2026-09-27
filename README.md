# Signal — AI Resume & Interview Coach

A single-page tool that reads a resume against a target job role and returns three things a
recruiter would normally take a week to tell you: what's working, what keywords are missing,
and three interview questions built from the actual gaps in that resume.

Built for **Campulsy Hack Days (MLH & Google Gemini)**.

## Why this exists

Most resume checkers either (a) run a generic ATS keyword match with no reasoning, or
(b) wrap a chatbot around the resume and call it a feature. This project uses Gemini as the
core engine, not a bolt-on: every strength, gap, and interview question on screen is generated
live from the resume text you paste in — nothing is hardcoded or templated.

## Architecture

```
Input Layer (HTML form)
   │  name, target role, resume text, API key
   ▼
Prompt Builder (JS)
   │  wraps resume + role into a structured prompt that forces JSON output
   ▼
Gemini 2.5 Flash  (generativelanguage.googleapis.com REST endpoint)
   │  returns { strengths[], missing_keywords[], interview_questions[] }
   ▼
Render Layer (JS)
   │  parses JSON, fills three tabbed cards
   ▼
Output: Strengths / Gaps / Interview Qs tabs
```

No backend, no build step — the whole app is `index.html`. The Gemini call is a direct
`fetch()` to the REST endpoint, which is exactly what the hackathon blueprint's "Frontend
Option A" calls for.

## Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Open `index.html` in any browser (or serve it: `python3 -m http.server` from this folder).
3. Paste the API key into the form — it's kept in memory in your browser tab only and is sent
   directly to Google's API, never stored or logged anywhere else.
4. Paste a resume, type a target role, click **Analyze resume**.

No `npm install`, no `.env` file required for the demo — the key is entered at runtime so
judges can test it instantly with their own key.

## Proof of Gemini API usage

The core logic lives in `callGemini()` in `index.html`. It calls
`models/gemini-2.5-flash:generateContent` with a prompt that forces the model to reason about
the specific resume text and target role, then return structured JSON that the UI renders
directly — remove the API call and the app has nothing left to show.

## What's next (if this moves past the hackathon)

- Move the API key server-side so it's never exposed in the client.
- Support PDF/DOCX resume upload instead of paste-only.
- Score resumes against a real job description, not just a role title.

## Security note

Never commit a real API key to this repo. If you deploy this, move the Gemini call to a small
backend (or Cloud Function) and keep the key in an environment variable / Secret Manager.
