
import streamlit as st
import hashlib
import cv2
import numpy as np
import tempfile
import os
from utils import (
    get_video_basic_info,
    extract_keyframes_every_n_seconds,
    compute_blur_scores,
    file_sha256,
    read_metadata_hachoir,
    extract_audio_waveform,
    plot_waveform,
    plot_spectrogram,
)

st.set_page_config(page_title="Video Authenticity Toolkit", layout="wide")

# iOS-friendly instructions
st.markdown("""
<style>
/* Make touch targets comfy on mobile */
button[kind="primary"], .stButton>button { padding: 0.8rem 1.1rem; font-size: 1rem; }
</style>
<link rel="apple-touch-icon" href="https://static.streamlit.io/favicon.svg">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
""", unsafe_allow_html=True)

st.title("🎛️ Video Authenticity Toolkit (Web)")
st.write("""
A browser-based, privacy-friendly app to help you **assess whether a video looks authentic or manipulated**.
It does **not** claim to detect deepfakes with certainty; instead it gathers clues:
**metadata, keyframes, blur/lighting changes, hashes, audio patterns** and a practical **checklist**.
""")

with st.expander("What this does (and doesn't)", expanded=False):
    st.markdown("""
- **Does:**  
  - Reads **basic metadata** (codec, duration, resolution, FPS).  
  - Extracts **key frames** every *N* seconds for manual review & reverse image search.  
  - Calculates **blur/sharpness scores** (sudden spikes can hint at edits).  
  - Generates a **SHA-256 hash** of the file.  
  - Displays **audio waveform & spectrogram** for abrupt cuts.  
- **Doesn't:**  
  - Give an automatic 'real/fake' verdict or upload your file to third parties.
""")

uploaded = st.file_uploader("Upload a video (MP4/MOV/AVI/MKV)", type=["mp4","mov","avi","mkv"])
n_seconds = st.number_input("Extract a frame every N seconds", min_value=1, max_value=30, value=3, step=1)
run_btn = st.button("Run analysis")

if uploaded and run_btn:
    with st.spinner("Saving file..."):
        tdir = tempfile.TemporaryDirectory()
        video_path = os.path.join(tdir.name, uploaded.name)
        with open(video_path, "wb") as f:
            f.write(uploaded.read())

    sha = file_sha256(video_path)
    info = get_video_basic_info(video_path)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 File & Technical Info")
        st.write(f"**Filename:** {os.path.basename(video_path)}")
        st.write(f"**SHA-256:** `{sha}`")
        if info:
            st.write(f"**Resolution:** {info['width']} × {info['height']}")
            st.write(f"**FPS:** {info['fps']:.2f}")
            st.write(f"**Duration:** {info['duration_sec']:.2f} sec")
            st.write(f"**Total Frames (approx):** {info['frame_count']}")
        else:
            st.warning("Couldn't read video info via OpenCV.")

        with st.expander("Raw metadata (Hachoir)", expanded=False):
            meta = read_metadata_hachoir(video_path)
            if meta:
                st.json(meta)
            else:
                st.info("No readable metadata found (common for social uploads).")

    with col2:
        st.subheader("🎞️ Keyframes & Blur Scores")
        frames, timestamps = extract_keyframes_every_n_seconds(video_path, n_seconds=n_seconds, limit=120)
        if frames:
            blur_scores = compute_blur_scores(frames)
            cols = st.columns(3)
            for i, (img, ts, score) in enumerate(zip(frames, timestamps, blur_scores)):
                with cols[i % 3]:
                    st.image(img, caption=f"t={ts:.1f}s | blur={score:.1f}", use_column_width=True)
            st.caption("Tip: Sudden spikes/dips in sharpness can hint at splices, composites, or re-encodes.")
        else:
            st.warning("No frames extracted. The video may be too short or unreadable.")

    st.subheader("🔊 Audio Inspection")
    try:
        wav_path, sr, y = extract_audio_waveform(video_path)
        if y is not None and len(y) > 0:
            st.write(f"Sample rate: {sr} Hz")
            wf_fig = plot_waveform(y, sr)
            st.pyplot(wf_fig, clear_figure=True)
            spec_fig = plot_spectrogram(y, sr)
            st.pyplot(spec_fig, clear_figure=True)
            st.caption("Look for abrupt silence, copy-paste patterns, or mismatched noise floors between cuts.")
        else:
            st.info("No audio stream found or couldn't extract audio.")
    except Exception as e:
        st.info(f"Audio analysis skipped: {e}")

    st.subheader("🧰 Investigation Checklist")
    st.markdown("""
- ✅ **Context check:** Search reputable news for matching date/place.  
- 🔎 **Reverse search:** Screenshot key frames → Google Lens/TinEye.  
- 👀 **Visual seams:** Warped backgrounds, inconsistent shadows, odd reflections.  
- 🧍 **Faces/hands:** Teeth, ears, fingers often glitch in AI videos.  
- 🎧 **Audio:** Consistent ambience/noise floor across cuts?  
- 🗂️ **Metadata:** Plausible camera info & creation time?  
- 🧾 **Source:** Who posted first? Primary/original upload available?
    """)

    st.success("Analysis complete. Use the frames and plots above for manual verification and reverse searches.")
    st.caption("Pro tip: Save the SHA-256 alongside your notes so others can reproduce your findings.")
else:
    st.info("Upload a video and tap **Run analysis** to begin.")
