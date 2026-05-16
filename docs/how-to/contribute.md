# Contributing Workflow

This project uses a small, explicit workflow so changes stay reviewable and easy to deploy.

## Branch naming

Create focused branches using one of these prefixes:

- `feature/<topic>`
- `fix/<topic>`
- `docs/<topic>`

Examples:

- `feature/voice-followups`
- `fix/admin-preview-guard`
- `docs/vercel-preview`

## Commit format

Use Conventional Commits:

```text
<type>(<scope>): <short summary>
```

Common examples for this repo:

- `feat(chat): improve grounded answer routing`
- `feat(voice): add hosted preview safeguards`
- `docs(readme): link Diataxis docs set`
- `chore(vercel): add preview deployment config`

Recommended commit types:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

## Before pushing

Run the minimum validation set:

```powershell
python -m pytest
```

If your change affects hosted preview behavior, also confirm:

- public student chat still loads
- `/api/chat` still returns grounded responses
- admin behavior is correct for the chosen mode

## Pull request expectations

Open a draft PR when:

- the change touches multiple subsystems
- deployment behavior changes
- environment variable requirements change

Include in the PR description:

- what changed
- why it changed
- how you verified it
- any new env vars or deployment assumptions

## GitHub and Vercel relationship

GitHub is the source of truth for code history.
Vercel preview deployments should be triggered from Git pushes or PR branches after the repo is connected to a Vercel project.
