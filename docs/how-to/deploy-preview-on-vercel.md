# Deploy Preview on Vercel

This guide covers the intended phase-1 deployment path: a hosted student-chat preview, not a production-grade admin system.

## What the preview is

The Vercel preview is designed to:

- serve the student chat UI
- answer from seeded sample knowledge
- run in hosted demo mode
- avoid implying persistent admin uploads or durable local storage

## What the preview is not

The phase-1 preview does not promise:

- persistent SQLite data
- durable uploaded document storage
- hosted admin knowledge management

## 1. Prepare the repository

Initialize and commit locally if you have not done so already:

```powershell
git init
git branch -M main
git add .
git commit -m "feat(platform): add vercel preview workflow and maintainer docs"
```

Then connect the repository to GitHub using your preferred GitHub workflow.

## 2. Link the project to Vercel

From the project root:

```powershell
vercel
```

Or use deterministic linking if you already know the project and team:

```powershell
vercel link --yes --project <project-name-or-id> --scope <team>
```

## 3. Configure environment variables

At minimum, set these for preview:

- `SECRET_KEY`
- `DEMO_MODE=1`
- `VOICE_ENABLED=0`

Optional preview-safe AI settings:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `EMBEDDING_MODEL`

If you do not provide a live AI key, the preview still works using deterministic local retrieval and seeded content.

## 4. Deploy

Use either:

```powershell
vercel
```

or Git-linked preview deployments after the repo is connected.

## 5. Verify the deployment

Check:

- `/` loads successfully
- asking `What is the admission process?` returns a valid answer
- admin routes show the hosted-demo restriction message
- voice is hidden or disabled unless you intentionally configured it

## Runtime notes

- Vercel-hosted demo mode uses a writable temporary runtime directory
- static assets are served from `public/**`
- top-level Flask deployment uses [app.py](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/app.py)
- preview data is intentionally non-persistent by design
