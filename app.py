
import streamlit as st
import tempfile, os, hashlib, cv2, numpy as np

from utils import (
    file_sha256,
    get_video_basic_info,
    extract_keyframes_every_n_seconds,
    compute_blur_scores,
    read_metadata_hachoir,
    extract_audio_waveform,
    plot_waveform,
    plot_spectrogram,
)

st.set_page_config(page_title="Video Authenticity Toolkit", layout="wide")
st.title("🎥 Video Authenticity Toolkit")

st.write("Upload a video to analyze metadata, extract frames, and inspect audio patterns.")

uploaded = st.file_uploader("Choose a video", type=["mp4","mov","avi","mkv"])
n_seconds = st.number_input("Extract a frame every N seconds", min_value=1, max_value=30, value=3, step=1)
run = st.button("Run analysis")

if uploaded and run:
    with st.spinner("Saving video..."):
        tdir = tempfile.TemporaryDirectory()
        vpath = os.path.join(tdir.name, uploaded.name)
        with open(vpath, "wb") as f:
            f.write(uploaded.read())

    # Hash & basics
    sha = file_sha256(vpath)
    info = get_video_basic_info(vpath)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📄 File & Technical Info")
        st.write(f"**Filename:** {os.path.basename(vpath)}")
        st.write(f"**SHA-256:** `{sha}`")
        if info:
            st.write(f"**Resolution:** {info['width']} × {info['height']}")
            st.write(f"**FPS:** {info['fps']:.2f}")
            st.write(f"**Duration:** {info['duration_sec']:.2f} sec")
            st.write(f"**Total Frames (approx):** {info['frame_count']}")
        else:
            st.warning("Couldn't read basic info via OpenCV.")

        with st.expander("Raw metadata (Hachoir)"):
            meta = read_metadata_hachoir(vpath)
            if meta:
                st.json(meta)
            else:
                st.info("No readable metadata found (common for social uploads).")

    with c2:
        st.subheader("🎞️ Keyframes & Blur Scores")
        frames, ts = extract_keyframes_every_n_seconds(vpath, n_seconds=n_seconds, limit=120)
        if frames:
            scores = compute_blur_scores(frames)
            cols = st.columns(3)
            for i, (img, tstamp, sc) in enumerate(zip(frames, ts, scores)):
                with cols[i % 3]:
                    st.image(img, use_column_width=True, caption=f"t={tstamp:.1f}s | blur={sc:.1f}")
            st.caption("Tip: Large jumps/dips in sharpness may hint at edits/compositing or re-encodes.")
        else:
            st.warning("No frames extracted. Video may be too short or unreadable.")

    st.subheader("🔊 Audio inspection")
    try:
        wav_path, sr, y = extract_audio_waveform(vpath)
        if y is not None and len(y) > 0:
            st.write(f"Sample rate: {sr} Hz")
            wf = plot_waveform(y, sr)
            st.pyplot(wf, clear_figure=True)
            spec = plot_spectrogram(y, sr)
            st.pyplot(spec, clear_figure=True)
            st.caption("Look for abrupt silence, copy‑paste patterns, or mismatched noise floors between cuts.")
        else:
            st.info("No audio stream found or couldn't extract audio (ffmpeg may be missing).")
    except Exception as e:
        st.info(f"Audio analysis skipped: {e}")

    st.subheader("🧰 Investigation checklist")
    st.markdown("""
- ✅ **Context**: Does reputable news match the date/place?
- 🔎 **Reverse search**: Screenshot keyframes → Google Lens/TinEye.
- 👀 **Visual seams**: Warped backgrounds, mismatched shadows/reflections.
- 🧍 **Faces/Hands**: Unnatural blinking, teeth/ear/finger glitches.
- 🎧 **Audio**: Consistent ambience/noise floor across cuts?
- 🗂️ **Metadata**: Plausible camera info & creation time?
- 🧾 **Source**: Who posted first? Any original upload?
    """)

else:
    st.info("Upload a video and press **Run analysis**.")
