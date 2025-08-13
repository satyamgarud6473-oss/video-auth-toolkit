
# Video Authenticity Toolkit – Full App

This is the **full working Streamlit app** (drop-in replacement for your placeholder).
- Keyframes every N seconds + blur scores
- SHA-256 hash & basic video info
- Hachoir metadata (if present)
- Audio waveform & spectrogram (needs ffmpeg on server; gracefully skips otherwise)

## Deploy
1. Replace your repo's `app.py`, `utils.py`, and `requirements.txt` with these versions.
2. Commit changes.
3. In Streamlit Cloud, click **Manage app → Deploy** (or it auto-rebuilds).

## Note
If audio plots don't show, install ffmpeg on the host. Streamlit Cloud may not have it by default; the app will still work (video features).
