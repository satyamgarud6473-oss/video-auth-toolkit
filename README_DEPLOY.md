
# Video Authenticity Toolkit – Web (iOS-friendly)

This is a **hosted** version of the Video Authenticity Toolkit that runs in the browser (works great on iPhone Safari).  
It’s a Streamlit app you can deploy to **Hugging Face Spaces** (easiest), **Render.com**, or any Docker host.

---

## 🚀 Option A — Deploy on Hugging Face Spaces (fastest)

1. Create a free account at Hugging Face.
2. Create a new **Space** and choose **Streamlit** as SDK.
3. Upload these files (or connect this folder as a Git repo).
4. Wait for the build → Open the Space URL.

**iPhone tip:** Open the Space URL in Safari → Share → *Add to Home Screen* for an app-like icon.

---

## 🚀 Option B — Deploy on Render.com (Docker)

1. Push this folder to a Git repository.
2. On Render, **New + Web Service** → Select your repo.
3. Environment: **Docker**.
4. Render will auto-detect the Dockerfile.
5. Once deployed, open the URL on your iPhone and *Add to Home Screen*.

---

## 🧱 Local run

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
```

---

## ⚙️ Notes

- **Privacy:** Files are processed on the server you control. For sensitive content, prefer self-hosting.
- **Audio extraction:** Requires `ffmpeg` on the server (HF Spaces provides it; otherwise install).
- **No "fake/real" verdict:** This tool provides artifacts & checks to help you judge authenticity.

