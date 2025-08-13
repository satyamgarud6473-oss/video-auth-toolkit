import streamlit as st
import os
import hashlib

# --- Safe imports ---
try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    from hachoir.parser import createParser
    from hachoir.metadata import extractMetadata
except ImportError:
    createParser = None
    extractMetadata = None

try:
    import ffmpeg
except ImportError:
    ffmpeg = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

try:
    from scipy.io import wavfile
except ImportError:
    wavfile = None


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


st.title("🎥 Video Authenticity Toolkit — Error-Proof Version")
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    temp_path = os.path.join("temp_video", uploaded_file.name)
    os.makedirs("temp_video", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.subheader("File Information")
    st.write(f"**File name:** {uploaded_file.name}")
    st.write(f"**SHA-256 hash:** {calculate_sha256(temp_path)}")

    # --- Metadata extraction ---
    st.subheader("Metadata Extraction")
    if createParser and extractMetadata:
        parser = createParser(temp_path)
        if parser:
            metadata = extractMetadata(parser)
            if metadata:
                for item in metadata.exportPlaintext():
                    st.write(item)
            else:
                st.write("No metadata found.")
        else:
            st.write("Could not parse video metadata.")
    else:
        st.warning("⚠️ Metadata feature skipped — hachoir not installed.")

    # --- Frame analysis ---
    st.subheader("Frame Analysis")
    if cv2 and np:
        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            st.error("Could not open video.")
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            st.write(f"**FPS:** {fps}")
            st.write(f"**Total frames:** {frame_count}")
            st.write(f"**Duration (sec):** {frame_count / fps if fps else 'Unknown'}")
            cap.release()
    else:
        st.warning("⚠️ Frame analysis skipped — OpenCV/Numpy not installed.")

    # --- Audio analysis ---
    st.subheader("Audio Analysis")
    if AudioSegment and ffmpeg:
        try:
            audio = AudioSegment.from_file(temp_path)
            st.write(f"Audio channels: {audio.channels}, Frame rate: {audio.frame_rate}")
        except Exception as e:
            st.error(f"Audio extraction failed: {e}")
    else:
        st.warning("⚠️ Audio analysis skipped — ffmpeg/pydub not installed.")
