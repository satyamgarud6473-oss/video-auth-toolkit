
import cv2
import numpy as np
import hashlib
import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import tempfile
import math
import matplotlib.pyplot as plt
from pydub import AudioSegment

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def get_video_basic_info(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_sec = frame_count / fps if fps > 0 else 0.0
    cap.release()
    return {
        "fps": float(fps),
        "width": w,
        "height": h,
        "frame_count": frame_count,
        "duration_sec": float(duration_sec),
    }

def extract_keyframes_every_n_seconds(path, n_seconds=3, limit=120):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return [], []
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25.0
    frames = []
    timestamps = []
    step = int(max(1, round(fps * n_seconds)))
    idx = 0
    while len(frames) < limit:
        ret = cap.grab()
        if not ret:
            break
        if idx % step == 0:
            ret2, frame = cap.retrieve()
            if not ret2:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(rgb)
            timestamps.append(idx / fps)
        idx += 1
    cap.release()
    return frames, timestamps

def compute_blur_scores(frames):
    scores = []
    for f in frames:
        gray = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        scores.append(float(score))
    return scores

def read_metadata_hachoir(path):
    try:
        parser = createParser(path)
        if not parser:
            return {}
        with parser:
            metadata = extractMetadata(parser)
        if not metadata:
            return {}
        data = {}
        for item in metadata.exportDictionary():
            data.update(item)
        return data
    except Exception:
        return {}

def extract_audio_waveform(video_path):
    """Extract audio using pydub (requires ffmpeg). Returns (wav_path, sample_rate, samples ndarray)."""
    try:
        audio = AudioSegment.from_file(video_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        samples = samples / (2**15)
        sr = audio.frame_rate
        tdir = tempfile.mkdtemp()
        wav_path = os.path.join(tdir, "audio_mono16k.wav")
        audio.export(wav_path, format="wav")
        return wav_path, sr, samples
    except Exception:
        return None, None, None

def plot_waveform(samples, sr):
    import matplotlib.pyplot as plt
    import numpy as np
    fig = plt.figure()
    t = np.arange(len(samples)) / sr
    plt.plot(t, samples)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Audio Waveform")
    plt.tight_layout()
    return fig

def plot_spectrogram(samples, sr, nfft=512, hop=256):
    import matplotlib.pyplot as plt
    import numpy as np
    fig = plt.figure()
    if len(samples) < nfft:
        plt.title("Spectrogram (not enough samples)")
        return fig
    window = np.hanning(nfft)
    frames = []
    for start in range(0, len(samples)-nfft, hop):
        segment = samples[start:start+nfft] * window
        spec = np.fft.rfft(segment)
        frames.append(np.abs(spec)**2)
    S = np.array(frames).T + 1e-10
    plt.imshow(10*np.log10(S), aspect="auto", origin="lower",
               extent=[0, len(samples)/sr, 0, sr/2])
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Spectrogram (Power dB)")
    plt.tight_layout()
    return fig
