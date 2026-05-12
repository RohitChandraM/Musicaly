# Vocal Humanizer AI

> **One-click polish for AI vocals.**

Upload an AI-generated vocal stem or full mixed song and get back a warmer, less synthetic, more naturally mixed result — in seconds.

---

## What it does

| Processing stage | Effect |
|---|---|
| High-pass filter | Removes rumble / low-end mud |
| Body EQ boost (150–250 Hz) | Adds warmth and chest resonance |
| Mud cut (350–600 Hz) | Clears boxiness |
| Nasal cut (800 Hz–1.5 kHz) | Reduces the "AI robot" tone |
| Dynamic harshness reduction (2.5–5 kHz) | Softens harsh peaks without killing presence |
| De-esser (5–8.5 kHz) | Controls sharp S and T sounds |
| Soft saturation | Adds subtle harmonic colour (tanh curve) |
| Short room ambience | Places the vocal in a real-sounding space |
| Loudness normalization | Targets –14 LUFS streaming level |
| True-peak limiter | Keeps output below –1 dBTP |

---

## Presets

| Preset | Best for |
|---|---|
| **Natural** | Any AI vocal — subtle, transparent, realistic |
| **Warm** | Sad/romantic, Hindi, Telugu, melodic songs |
| **Rap / Punchy** | Rap, drill, trap — tight, upfront, controlled |

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + Tailwind CSS + Vite |
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Audio processing | librosa · numpy · scipy · pedalboard |
| Format conversion | FFmpeg |
| Stem separation (optional) | Demucs |

---

## Requirements

- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg** installed and on `$PATH`

### Check FFmpeg

```bash
ffmpeg -version
```

If not installed:
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/rohitchandram/musicaly.git
cd musicaly
```

### 2. Set up the Python backend

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up the React frontend

```bash
cd frontend
npm install
```

---

## Running locally

### Start the backend

```bash
# From the repo root (with venv activated)
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Swagger docs: `http://localhost:8000/docs`

### Start the frontend

```bash
# In a separate terminal, from repo root
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Optional: Enable full-song stem separation

Full-song mode separates vocals from the instrumental using **Demucs** before processing.

```bash
pip install demucs
```

> **Note:** Demucs downloads a ~300 MB model on first run. Requires a decent GPU or will be slow on CPU.

Without Demucs installed, uploading a full song will automatically fall back to processing the entire file as a vocal stem with a warning shown in the UI.

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/upload` | POST | Upload audio file. Returns `file_id`. |
| `/process` | POST | Start processing job. Returns `job_id`. |
| `/status/{job_id}` | GET | Poll job status and progress (0–100%). |
| `/download/{file_id}` | GET | Download processed file. `?fmt=wav` or `?fmt=mp3` |
| `/health` | GET | Health check. |

### POST /process body

```json
{
  "file_id": "uuid-string",
  "input_type": "auto",
  "preset": "natural",
  "strength": 0.75
}
```

- `input_type`: `"auto"` | `"vocal_stem"` | `"full_song"`
- `preset`: `"natural"` | `"warm"` | `"rap_punchy"`
- `strength`: `0.25` | `0.5` | `0.75` | `1.0`

---

## File size limits

- Maximum upload: **200 MB**
- Processed files are automatically deleted after **1 hour**

---

## Project structure

```
musicaly/
├── backend/
│   ├── main.py              # FastAPI app + endpoints
│   ├── upload_handler.py    # File upload, validation, temp storage
│   ├── processing_chain.py  # Full DSP chain (EQ, dynamics, saturation, reverb)
│   ├── presets.py           # Preset configs + strength scaling
│   ├── stem_separator.py    # Demucs integration (optional)
│   └── export_handler.py    # WAV / MP3 export via soundfile + FFmpeg
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main application
│   │   └── components/
│   │       ├── UploadArea.jsx          # Drag-and-drop upload
│   │       ├── PresetSelector.jsx      # Preset cards
│   │       ├── StrengthSlider.jsx      # Strength selector
│   │       ├── InputTypeSelector.jsx   # Vocal stem / full song / auto
│   │       ├── AudioPlayer.jsx         # Before / after player
│   │       ├── ProgressBar.jsx         # Job progress indicator
│   │       └── DownloadButtons.jsx     # WAV + MP3 download
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── requirements.txt
└── README.md
```

---

## License

MIT — use freely, no paid plugins required.
