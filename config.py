"""
Google Meet Summarizer - Configuration
======================================
Central configuration file for all settings and API keys.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# DIRECTORY CONFIGURATION
# =============================================================================

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Storage directories
RECORDINGS_DIR = BASE_DIR / "recordings"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
SUMMARIES_DIR = BASE_DIR / "summaries"

# Create directories if they don't exist
for directory in [RECORDINGS_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
    directory.mkdir(exist_ok=True)

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================

# Audio recording settings
SAMPLE_RATE = 44100  # Hz - CD quality audio
CHANNELS = 2         # Stereo recording
DTYPE = "int16"      # Audio data type

# =============================================================================
# WHISPER CONFIGURATION
# =============================================================================

# Whisper model size
# Options: "tiny", "base", "small", "medium", "large"
# Larger models are more accurate but slower and require more memory
# - tiny:   ~1GB RAM, fastest, least accurate
# - base:   ~1GB RAM, good balance for English
# - small:  ~2GB RAM, good for most languages
# - medium: ~5GB RAM, very accurate
# - large:  ~10GB RAM, most accurate
WHISPER_MODEL = "base"

# =============================================================================
# GEMINI API CONFIGURATION
# =============================================================================

# Get your API key from: https://makersuite.google.com/app/apikey
# Set it as an environment variable: GEMINI_API_KEY=your-key-here
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini model to use
GEMINI_MODEL = "gemini-pro"

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# App metadata
APP_NAME = "Google Meet Summarizer"
APP_VERSION = "1.0.0"
APP_ICON = "🎤"

# Summary prompt template
SUMMARY_PROMPT = """
You are an expert meeting analyst. Analyze the following meeting transcript and provide a comprehensive, well-structured summary.

## TRANSCRIPT:
{transcript}

## INSTRUCTIONS:
Please provide your summary in the following format:

### 📋 Meeting Overview
Provide a brief 2-3 sentence overview of what this meeting was about.

### 🎯 Key Discussion Points
List the main topics and points discussed during the meeting as bullet points.

### ✅ Action Items
List specific tasks that need to be done, with the person responsible if mentioned.
Format: - [ ] Task description (Assigned to: Name, if known)

### 🔔 Decisions Made
List any decisions that were made during the meeting.

### 📅 Follow-up Items
List any items that need follow-up or future discussion.

### 💡 Key Insights
Any important insights, concerns, or notable moments from the meeting.

---
Please be thorough but concise. Focus on the most important information that attendees would need to reference later.
"""
