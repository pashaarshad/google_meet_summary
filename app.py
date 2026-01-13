import streamlit as st
import sounddevice as sd
import soundfile as sf
import whisper
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import tempfile
import os

# ----------------------------
# Config
# ----------------------------
SAMPLE_RATE = 16000
CHANNELS = 1
WHISPER_MODEL = "base"
LLM_MODEL = "microsoft/phi-3-mini-4k-instruct"  # CPU friendly

# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Meeting Summarizer", layout="centered")
st.title("🎙️ Meeting Transcript & Summarizer")
st.caption("Free • Open Source • Google Meet Compatible")

duration = st.slider("Recording duration (minutes)", 5, 120, 30)

# ----------------------------
# Audio Recording
# ----------------------------
if st.button("▶️ Start Recording"):
    st.info("Recording system audio... Join your Google Meet now.")

    audio = sd.rec(
        int(duration * 60 * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )
    sd.wait()

    tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp_audio.name, audio, SAMPLE_RATE)

    st.success("Recording completed")
    st.session_state["audio_file"] = tmp_audio.name

# ----------------------------
# Transcription
# ----------------------------
if "audio_file" in st.session_state and st.button("🧠 Transcribe Meeting"):
    st.info("Transcribing audio...")
    whisper_model = whisper.load_model(WHISPER_MODEL)

    result = whisper_model.transcribe(st.session_state["audio_file"])
    transcript = result["text"]

    st.session_state["transcript"] = transcript
    st.success("Transcription completed")

    st.subheader("📄 Transcript")
    st.text_area("", transcript, height=250)

# ----------------------------
# Summarization
# ----------------------------
if "transcript" in st.session_state and st.button("✍️ Summarize Meeting"):
    st.info("Loading summarization model...")

    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )

    prompt = f"""
Summarize the following meeting in 5 bullet points.
Highlight key decisions and action items.

Meeting transcript:
{st.session_state['transcript']}
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.2
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    st.session_state["summary"] = summary

    st.success("Summary generated")

    st.subheader("📋 Meeting Summary")
    st.text_area("", summary, height=200)

# ----------------------------
# Downloads
# ----------------------------
if "transcript" in st.session_state:
    st.download_button(
        "⬇️ Download Transcript",
        st.session_state["transcript"],
        file_name="meeting_transcript.txt"
    )

if "summary" in st.session_state:
    st.download_button(
        "⬇️ Download Summary",
        st.session_state["summary"],
        file_name="meeting_summary.txt"
    )
