"""
Google Meet Summarizer - Main Application
==========================================
Streamlit web application for recording, transcribing, and summarizing meetings.
"""

import streamlit as st
import time
from pathlib import Path
from datetime import datetime
import os

# Import custom modules
from audio_recorder import AudioRecorder, list_audio_devices
from transcriber import Transcriber
from summarizer import Summarizer
from config import (
    APP_NAME, APP_VERSION, APP_ICON,
    RECORDINGS_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR,
    GEMINI_API_KEY
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Card styling */
    .status-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-card h3 {
        color: #1a1a2e !important;
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }
    
    .status-card p {
        color: #333333 !important;
        margin: 0.3rem 0;
        font-size: 1rem;
    }
    
    .recording-active {
        background: #ffe8e8;
        border-left-color: #e74c3c;
        animation: pulse 2s infinite;
    }
    
    .recording-active h3 {
        color: #c0392b !important;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    /* Progress indicator */
    .processing-indicator {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 1rem;
        background: #e8f4f8;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'recorder' not in st.session_state:
    st.session_state.recorder = AudioRecorder()
    
if 'transcriber' not in st.session_state:
    st.session_state.transcriber = None  # Lazy load (heavy model)
    
if 'summarizer' not in st.session_state:
    st.session_state.summarizer = Summarizer()
    
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

if 'current_transcript' not in st.session_state:
    st.session_state.current_transcript = ""
    
if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""
    
if 'last_audio_file' not in st.session_state:
    st.session_state.last_audio_file = ""
    
if 'recording_start_time' not in st.session_state:
    st.session_state.recording_start_time = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_transcriber():
    """Lazy load the Whisper model."""
    if st.session_state.transcriber is None:
        with st.spinner("🔄 Loading Whisper model (first time only)..."):
            st.session_state.transcriber = Transcriber()
    return st.session_state.transcriber


def format_duration(seconds):
    """Format seconds to MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def get_recording_stats():
    """Get statistics about recordings."""
    recordings = list(RECORDINGS_DIR.glob("*.wav"))
    transcripts = list(TRANSCRIPTS_DIR.glob("*.txt"))
    summaries = list(SUMMARIES_DIR.glob("*.md"))
    return len(recordings), len(transcripts), len(summaries)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown(f"## {APP_ICON} {APP_NAME}")
    st.markdown(f"*Version {APP_VERSION}*")
    st.divider()
    
    # API Status
    st.markdown("### 🔑 API Status")
    if st.session_state.summarizer.is_configured():
        st.success("✅ Gemini API Connected")
    else:
        st.warning("⚠️ Gemini API Not Configured")
        st.markdown("""
        **To enable AI summaries:**
        1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Create a `.env` file with:
        ```
        GEMINI_API_KEY=your-key
        ```
        3. Restart the app
        """)
    
    st.divider()
    
    # Statistics
    st.markdown("### 📊 Statistics")
    rec_count, trans_count, sum_count = get_recording_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🎤", rec_count, "Recordings")
    col2.metric("📝", trans_count, "Transcripts")
    col3.metric("📋", sum_count, "Summaries")
    
    st.divider()
    
    # Audio Device Selection
    st.markdown("### 🎧 Audio Settings")
    
    try:
        devices = st.session_state.recorder.get_audio_devices()
        if devices:
            device_names = [f"{d['id']}: {d['name']}" for d in devices]
            selected_device = st.selectbox(
                "Select Audio Input",
                options=range(len(devices)),
                format_func=lambda x: device_names[x],
                help="Select the audio device to record from. For system audio, select 'Stereo Mix' or virtual audio cable."
            )
            st.session_state.recorder.set_device(devices[selected_device]['id'])
        else:
            st.error("No audio input devices found!")
    except Exception as e:
        st.error(f"Error loading audio devices: {e}")
    
    st.divider()
    
    # Quick Links
    st.markdown("### 📁 Quick Links")
    if st.button("📂 Open Recordings Folder"):
        try:
            os.startfile(str(RECORDINGS_DIR))
        except Exception as e:
            st.error(f"Could not open folder: {e}")
    if st.button("📂 Open Transcripts Folder"):
        try:
            os.startfile(str(TRANSCRIPTS_DIR))
        except Exception as e:
            st.error(f"Could not open folder: {e}")
    if st.button("📂 Open Summaries Folder"):
        try:
            os.startfile(str(SUMMARIES_DIR))
        except Exception as e:
            st.error(f"Could not open folder: {e}")


# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🎤 Google Meet Summarizer</h1>
    <p>Record your meetings • Get AI-powered transcriptions • Generate smart summaries</p>
</div>
""", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3 = st.tabs(["🎙️ Record Meeting", "📜 History", "ℹ️ Help"])


# =============================================================================
# TAB 1: RECORD MEETING
# =============================================================================

with tab1:
    # Recording Controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎙️ Recording Controls")
        
        # Status indicator
        if st.session_state.is_recording:
            elapsed = time.time() - st.session_state.recording_start_time if st.session_state.recording_start_time else 0
            st.markdown(f"""
            <div style="background-color: #ffe8e8 !important; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #e74c3c; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <span style="display: block; color: #c0392b !important; margin: 0 0 0.5rem 0; font-size: 1.4rem; font-weight: 700;">🔴 Recording in Progress</span>
                <span style="display: block; color: #2d2d2d !important; margin: 0.3rem 0; font-size: 1.05rem;">Duration: <strong style="color: #c0392b !important;">{format_duration(elapsed)}</strong></span>
                <span style="display: block; color: #4a4a4a !important; margin: 0.3rem 0; font-size: 0.95rem;">Click "Stop Recording" when your meeting ends</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f0f4ff !important; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #667eea; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                <span style="display: block; color: #1a1a2e !important; margin: 0 0 0.5rem 0; font-size: 1.4rem; font-weight: 700;">⏸️ Ready to Record</span>
                <span style="display: block; color: #2d2d2d !important; margin: 0.3rem 0; font-size: 1.05rem;">Click "Start Recording" when your meeting begins</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Recording buttons
        col_start, col_stop = st.columns(2)
        
        with col_start:
            if st.button("🎤 Start Recording", 
                        disabled=st.session_state.is_recording,
                        use_container_width=True,
                        type="primary"):
                success = st.session_state.recorder.start_recording()
                if success:
                    st.session_state.is_recording = True
                    st.session_state.recording_start_time = time.time()
                    st.rerun()
                else:
                    st.error("Failed to start recording!")
        
        with col_stop:
            if st.button("⏹️ Stop Recording", 
                        disabled=not st.session_state.is_recording,
                        use_container_width=True,
                        type="secondary"):
                # Generate meeting name
                meeting_name = datetime.now().strftime("meeting_%Y%m%d_%H%M%S")
                
                with st.spinner("💾 Saving recording..."):
                    audio_path = st.session_state.recorder.stop_recording(meeting_name)
                
                if audio_path:
                    st.session_state.is_recording = False
                    st.session_state.last_audio_file = audio_path
                    st.session_state.recording_start_time = None
                    st.success(f"✅ Recording saved: {Path(audio_path).name}")
                    st.rerun()
                else:
                    st.error("Failed to save recording!")
    
    st.divider()
    
    # Processing Section
    if st.session_state.last_audio_file and not st.session_state.is_recording:
        st.markdown("### 🔄 Process Recording")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"📁 Last recording: **{Path(st.session_state.last_audio_file).name}**")
        
        with col2:
            process_btn = st.button("🚀 Transcribe & Summarize", 
                                   use_container_width=True, 
                                   type="primary")
        
        if process_btn:
            # Step 1: Transcribe
            progress = st.progress(0, text="🎯 Starting transcription...")
            
            try:
                transcriber = load_transcriber()
                progress.progress(20, text="📝 Transcribing audio (this may take a while)...")
                
                result = transcriber.transcribe(st.session_state.last_audio_file)
                st.session_state.current_transcript = result['text']
                
                progress.progress(60, text="🤖 Generating AI summary...")
                
                # Step 2: Summarize
                summary = st.session_state.summarizer.summarize(result['text'])
                st.session_state.current_summary = summary
                
                # Save files
                meeting_name = Path(st.session_state.last_audio_file).stem
                transcriber.transcribe_and_save(
                    st.session_state.last_audio_file, 
                    meeting_name
                )
                st.session_state.summarizer.summarize_and_save(
                    result['text'], 
                    meeting_name
                )
                
                progress.progress(100, text="✅ Complete!")
                time.sleep(0.5)
                progress.empty()
                
                st.success("✨ Transcription and summary complete!")
                
            except Exception as e:
                progress.empty()
                st.error(f"❌ Processing failed: {e}")
    
    st.divider()
    
    # Results Display
    if st.session_state.current_transcript or st.session_state.current_summary:
        st.markdown("### 📊 Results")
        
        result_tab1, result_tab2 = st.tabs(["📝 Transcript", "📋 Summary"])
        
        with result_tab1:
            if st.session_state.current_transcript:
                st.text_area(
                    "Full Transcript",
                    st.session_state.current_transcript,
                    height=300
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Transcript",
                        st.session_state.current_transcript,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )
                with col2:
                    if st.button("📋 Copy to Clipboard"):
                        st.code(st.session_state.current_transcript)
                        st.info("Select and copy the text above")
            else:
                st.info("No transcript available yet. Process a recording first!")
        
        with result_tab2:
            if st.session_state.current_summary:
                st.markdown(st.session_state.current_summary)
                
                st.download_button(
                    "📥 Download Summary",
                    st.session_state.current_summary,
                    file_name="summary.md",
                    mime="text/markdown"
                )
            else:
                st.info("No summary available yet. Process a recording first!")


# =============================================================================
# TAB 2: HISTORY
# =============================================================================

with tab2:
    st.markdown("### 📜 Meeting History")
    
    # List all summaries
    summaries = sorted(SUMMARIES_DIR.glob("*.md"), reverse=True)
    
    if summaries:
        for summary_file in summaries[:10]:  # Show last 10
            with st.expander(f"📋 {summary_file.stem}"):
                content = summary_file.read_text(encoding='utf-8')
                st.markdown(content)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download",
                        content,
                        file_name=summary_file.name,
                        mime="text/markdown",
                        key=f"dl_{summary_file.name}"
                    )
    else:
        st.info("No meeting summaries yet. Record and process your first meeting!")


# =============================================================================
# TAB 3: HELP
# =============================================================================

with tab3:
    st.markdown("""
    ### 📖 How to Use
    
    #### 1️⃣ Setup (First Time)
    1. **Install Virtual Audio Cable** (for system audio):
       - Windows: [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
       - Set it as your default playback device
       - Select it as input in this app
    
    2. **Configure Gemini API** (for AI summaries):
       - Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
       - Create `.env` file with `GEMINI_API_KEY=your-key`
    
    #### 2️⃣ Recording a Meeting
    1. Join your Google Meet
    2. Click **Start Recording** in this app
    3. When meeting ends, click **Stop Recording**
    4. Click **Transcribe & Summarize**
    
    #### 3️⃣ Output
    Your meeting will be:
    - 🎤 **Recorded** as WAV file
    - 📝 **Transcribed** to text
    - 📋 **Summarized** with key points, action items, and decisions
    
    ---
    
    ### ❓ FAQ
    
    **Q: Why is my recording silent?**  
    A: Make sure you've selected the correct audio input device. For system audio, use "Stereo Mix" or a virtual audio cable.
    
    **Q: Why is transcription slow?**  
    A: The Whisper model needs to process the entire audio file. Longer meetings take more time. Consider using the "tiny" model in config.py for faster (but less accurate) results.
    
    **Q: Can I use this offline?**  
    A: Transcription (Whisper) works offline. Summarization requires internet and Gemini API. Basic offline summaries are available as fallback.
    
    ---
    
    ### 🔧 Troubleshooting
    
    | Issue | Solution |
    |-------|----------|
    | No audio devices | Install audio drivers or virtual audio cable |
    | Transcription fails | Check audio file format (WAV) and quality |
    | Summary fails | Verify Gemini API key in .env file |
    | App crashes | Check terminal for error messages |
    """)


# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown(
    f"<center><small>{APP_NAME} v{APP_VERSION} • Made with ❤️ and AI</small></center>",
    unsafe_allow_html=True
)
