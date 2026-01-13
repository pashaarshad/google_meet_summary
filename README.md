# 🎤 Google Meet Summarizer

A powerful application that **records**, **transcribes**, and **summarizes** your Google Meet conversations using AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini-yellow.svg)

## ✨ Features

- 🎙️ **Audio Recording** - Capture system audio during Google Meet sessions
- 📝 **Transcription** - Convert speech to text using OpenAI Whisper (offline & free)
- 🤖 **AI Summarization** - Generate structured summaries using Google Gemini
- 📋 **Structured Output** - Get key points, action items, decisions, and follow-ups
- 🌐 **Web Interface** - Easy-to-use Streamlit dashboard
- 📁 **History** - Access past meeting summaries anytime

## 📋 Summary Output Includes

- 📋 **Meeting Overview** - Brief summary of the meeting
- 🎯 **Key Discussion Points** - Main topics covered
- ✅ **Action Items** - Tasks with assignees
- 🔔 **Decisions Made** - Important decisions
- 📅 **Follow-up Items** - Items for future discussion

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows/Mac/Linux
- Microphone or virtual audio cable (for system audio)

### Installation

1. **Clone or navigate to the project folder:**
   ```bash
   cd google_meet_summary
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Gemini API (for AI summaries):**
   
   Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   
   Create a `.env` file:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser at:** http://localhost:8501

---

## 🎧 Setting Up System Audio Recording

To record what you **hear** during Google Meet (not your microphone), you need a virtual audio cable:

### Windows

1. Download and install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
2. Set **CABLE Output** as your default playback device in Windows Sound Settings
3. In this app, select **CABLE Output** as the audio input

### Mac

1. Install [BlackHole](https://existential.audio/blackhole/)
2. Create a Multi-Output Device in Audio MIDI Setup
3. Select BlackHole as input in this app

### Linux

1. Use PulseAudio loopback module:
   ```bash
   pactl load-module module-loopback
   ```

---

## 📁 Project Structure

```
google_meet_summary/
├── app.py                 # Main Streamlit application
├── audio_recorder.py      # System audio capture module
├── transcriber.py         # Whisper transcription module
├── summarizer.py          # Gemini summarization module
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
├── .env.example           # Example environment file
├── README.md              # This file
├── recordings/            # Saved audio files
├── transcripts/           # Saved transcriptions
└── summaries/             # Saved meeting summaries
```

---

## 🔧 Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `WHISPER_MODEL` | `"base"` | Whisper model size (tiny/base/small/medium/large) |
| `SAMPLE_RATE` | `44100` | Audio sample rate in Hz |
| `CHANNELS` | `2` | Stereo (2) or Mono (1) |
| `GEMINI_MODEL` | `"gemini-pro"` | Gemini model to use |

### Whisper Model Comparison

| Model | Speed | Accuracy | RAM Required |
|-------|-------|----------|--------------|
| tiny | Fastest | Basic | ~1GB |
| base | Fast | Good | ~1GB |
| small | Medium | Better | ~2GB |
| medium | Slow | Great | ~5GB |
| large | Slowest | Best | ~10GB |

---

## 📖 Usage Guide

### Recording a Meeting

1. **Start the app:** `streamlit run app.py`
2. **Select your audio device** in the sidebar
3. **Join your Google Meet**
4. **Click "Start Recording"** when the meeting begins
5. **Click "Stop Recording"** when the meeting ends
6. **Click "Transcribe & Summarize"** to process

### Viewing History

- Go to the **History** tab to see past summaries
- Download summaries as Markdown files
- All files are saved in the `summaries/` folder

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| **No audio recorded** | Check audio device selection, ensure virtual audio cable is set up |
| **Transcription is slow** | Use a smaller Whisper model in config.py |
| **"API not configured"** | Add your Gemini API key to .env file |
| **Import errors** | Run `pip install -r requirements.txt` |
| **Recording fails** | Check if another app is using the microphone |

---

## 🔐 Privacy & Security

- ✅ **Transcription is 100% offline** - Audio never leaves your computer
- ✅ **Summaries use Gemini API** - Text is sent to Google for summarization
- ✅ **All files stored locally** - In the `recordings/`, `transcripts/`, `summaries/` folders
- ✅ **No data collection** - This app doesn't collect or send any analytics

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Google Gemini](https://ai.google.dev/) - AI summarization
- [Streamlit](https://streamlit.io/) - Web framework
- [SoundDevice](https://python-sounddevice.readthedocs.io/) - Audio recording

---

**Made with ❤️ for better meetings**
