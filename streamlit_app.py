import streamlit as st
from supabase import create_client, Client
import time
import os
import soundfile as sf
from io import BytesIO
import wave
import json
from vosk import Model, KaldiRecognizer

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="HealthGPT - Your Pocket Doctor", page_icon="🩺", layout="wide")

# ---------------- Supabase Initialization ----------------
SUPABASE_URL = "https://jnhfadolvhrwpnpjnwqw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpuaGZhZG9sdmhyd3BucGpud3F3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTU4NTkwMiwiZXhwIjoyMDc1MTYxOTAyfQ.I1Mdj6Sfej90o2zUEWN1qZwlX7MpzU8hdtQbhbMQnow"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "audio-stream"

# ---------------- Sidebar ----------------
st.sidebar.title("⚙️ Settings")
refresh_rate = st.sidebar.slider("Refresh every (seconds)", 1, 10, 3)
st.sidebar.info("This app listens for real-time audio uploads from ESP32 → Supabase → Vosk → HealthGPT.")

# ---------------- Header ----------------
st.markdown(
    """
    <h1 style='text-align:center; color:#2E86C1;'>🩺 HealthGPT - Your Pocket Doctor</h1>
    <p style='text-align:center; color:gray;'>AI-powered real-time symptom and medication analysis</p>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load Vosk Model ----------------
with st.spinner("🔄 Loading Vosk speech recognition model..."):
    vosk_model = Model(r"F:\Desktop\app - Copy\models\vosk-model-small-en-us-0.15")
st.success("✅ Vosk model loaded successfully!")

# ---------------- Helper Functions ----------------
def raw_to_wav(raw_bytes):
    """Convert raw PCM bytes to WAV format."""
    audio_array = []
    for i in range(0, len(raw_bytes), 2):  # 16-bit PCM
        val = int.from_bytes(raw_bytes[i:i+2], byteorder="little", signed=True)
        audio_array.append(val)
    wav_io = BytesIO()
    sf.write(wav_io, audio_array, 16000, format="WAV")
    wav_io.seek(0)
    return wav_io

def transcribe_vosk(wav_file):
    """Transcribe WAV audio to text using Vosk."""
    wf = wave.open(wav_file, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())
    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text += " " + res.get("text", "")
    res = json.loads(rec.FinalResult())
    text += " " + res.get("text", "")
    return text.strip()

# ---------------- UI Placeholders ----------------
status_placeholder = st.empty()
audio_col, text_col, ai_col = st.columns([1, 1, 1])
processed_files = set()

# ---------------- Main Loop ----------------
status_placeholder.info("⏳ Waiting for new audio uploads...")

while True:
    try:
        # List .raw files in Supabase bucket
        resp = supabase.storage.from_(BUCKET_NAME).list(path="")
        blobs = [f["name"] for f in resp if f["name"].endswith(".raw")]
        new_blobs = [b for b in blobs if b not in processed_files]

        if not new_blobs:
            status_placeholder.info("👂 Listening for new audio uploads...")
        else:
            for blob_name in new_blobs:
                try:
                    status_placeholder.warning(f"🎙 Processing: {blob_name}")

                    # Download raw file from Supabase
                    raw_bytes = supabase.storage.from_(BUCKET_NAME).download(blob_name)

                    # Convert -> WAV
                    wav_file = raw_to_wav(raw_bytes)

                    # Audio Column
                    audio_col.markdown("### 🔊 Recorded Audio")
                    audio_col.audio(wav_file, format="audio/wav")

                    # Transcribe
                    text_col.markdown("### 🗣 Transcribed Text")
                    transcribed_text = transcribe_vosk(wav_file)
                    text_col.success(transcribed_text if transcribed_text else "No speech detected.")

                    # AI Analysis
                    ai_col.markdown("### 🤖 HealthGPT Analysis")
                    try:
                        from your_healthgpt_module import analyze_text_with_gemini
                        analysis = analyze_text_with_gemini(transcribed_text)
                        ai_col.info(f"**Symptoms:** {', '.join(analysis.get('symptoms', []))}")
                        ai_col.success(f"**Medications:** {', '.join(analysis.get('medications', []))}")
                    except Exception as e:
                        ai_col.error(f"Gemini analysis failed: {e}")

                    processed_files.add(blob_name)
                    status_placeholder.success(f"✅ Processed {blob_name} successfully!")

                except Exception as e:
                    status_placeholder.error(f"Error processing {blob_name}: {e}")

        time.sleep(refresh_rate)

    except Exception as e:
        status_placeholder.error(f"Main loop error: {e}")
        time.sleep(5)
