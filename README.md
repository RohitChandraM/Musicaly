# Vocal Humanizer AI

> **One-click polish for AI vocals.**

Upload an AI-generated vocal stem or full mixed song and get back a warmer, less synthetic, more naturally mixed result.

## Quick start

```bash
# Backend
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173`.

## Requirements
- Python 3.10+
- Node.js 18+
- FFmpeg on `$PATH`

## Presets
| Preset | Best for |
|---|---|
| Natural | Any AI vocal — subtle, transparent |
| Warm | Sad/romantic, Hindi, Telugu, melodic |
| Rap / Punchy | Rap, drill, trap — tight and upfront |

## Optional: stem separation
```bash
pip install demucs
```
Without Demucs, full-song mode falls back to processing the whole file.

## API
| Endpoint | Method | Description |
|---|---|---|
| `/upload` | POST | Upload audio, returns `file_id` |
| `/process` | POST | Start job, returns `job_id` |
| `/status/{job_id}` | GET | Poll progress (0–100%) |
| `/download/{file_id}` | GET | Download WAV or MP3 (`?fmt=wav\|mp3`) |
