import streamlit as st

st.set_page_config(page_title="Video Authenticity Toolkit", layout="wide")
st.title("🎥 Video Authenticity Toolkit")

st.write("Upload a video to analyze metadata, extract frames, and inspect audio patterns.")

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    st.info("This is a demo placeholder. In the full version, video analysis features will appear here.")
