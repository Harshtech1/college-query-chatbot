# Local Setup Tutorial

This tutorial takes a first-time maintainer from a fresh checkout to a running local chatbot.

## 1. Prepare Python

Use standard Python `3.13`.

```powershell
py -3.13 --version
```

The project also includes a [.python-version](/D:/New_Volume_D/03_Projects/01_Active_Projects/Chatbot%20for%20College%20Queries/.python-version) file for hosted/runtime alignment.

## 2. Create and activate a virtual environment

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Create local environment settings

```powershell
Copy-Item .env.example .env
```

For a fully local run, keep:

- `DEMO_MODE=0`
- `VOICE_PROVIDER=stub` if you want local voice testing without a real API

## 5. Start the app

```powershell
python app.py
```

Open:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/admin/login`

Default admin credentials come from `.env`:

- username: `admin`
- password: `admin123`

## 6. Verify the app

Run the test suite:

```powershell
python -m pytest
```

Then check these flows manually:

- ask `What is the admission process?`
- ask a follow-up such as `What about eligibility?`
- log into the admin dashboard
- upload a small `.txt` document
- if voice is enabled locally, record a short sample question

## 7. Understand local data

Local development stores runtime state inside:

- `instance/college_chatbot.db`
- `instance/uploads/`

These paths are intentionally ignored by git and are not used as persistent storage in hosted preview mode.
