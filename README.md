# Chatbot for College Queries

A Flask-based university support chatbot with:

- student chat for admissions, fees, exams, attendance, courses, faculty, and timetable queries
- grounded FAQ-first and document-backed answers
- optional browser voice input and spoken replies
- local admin tools for FAQ editing and document ingestion
- Vercel-friendly hosted demo mode for preview deployments

## Quick Start

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open:

- Student chat: `http://127.0.0.1:5000/`
- Admin dashboard: `http://127.0.0.1:5000/admin/login`

Run tests:

```powershell
python -m pytest
```

## Documentation

- Tutorial: [Local setup](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/tutorials/local-setup.md)
- How-to: [Contributing workflow](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/how-to/contribute.md)
- How-to: [Deploy preview on Vercel](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/how-to/deploy-preview-on-vercel.md)
- Reference: [Configuration](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/reference/configuration.md)
- Reference: [Data model](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/reference/data-model.md)
- Explanation: [Architecture](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/docs/explanation/architecture.md)

## Deployment Notes

- Local development uses the Flask app directly from [app.py](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/app.py).
- Hosted preview mode targets Vercel and defaults to `DEMO_MODE=1` when running on Vercel.
- Static assets are served from `public/**` for Vercel compatibility.
- Hosted preview is intentionally non-persistent unless you provide your own external database and storage.

## Current Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: SQLite by default, MySQL-compatible via `DATABASE_URL`
- AI layer: OpenAI-compatible chat and embeddings
- Voice layer: stub, OpenAI-compatible, or ElevenLabs-compatible pipeline
- Preview hosting target: Vercel
