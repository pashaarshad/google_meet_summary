"""
Google Meet Summarizer - Transcription Module
==============================================
Handles speech-to-text conversion using OpenAI Whisper.
"""

import whisper
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import json
import tempfile
import os

from config import WHISPER_MODEL, TRANSCRIPTS_DIR


class Transcriber:
    """
    Transcribes audio files to text using OpenAI Whisper.
    
    Whisper is a free, offline speech recognition model that supports
    multiple languages and produces accurate transcriptions.
    
    Usage:
        transcriber = Transcriber()
        result = transcriber.transcribe("path/to/audio.wav")
        print(result['text'])
    """
    
    def __init__(self, model_name: str = WHISPER_MODEL):
        """
        Initialize the transcriber with specified Whisper model.
        
        Args:
            model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        
    def _load_model(self) -> None:
        """Load the Whisper model."""
        print(f"📥 Loading Whisper model: {self.model_name}...")
        self.model = whisper.load_model(self.model_name)
        print(f"✅ Whisper model loaded successfully!")
    
    def _load_audio_wav(self, audio_path: str) -> np.ndarray:
        """
        Load WAV audio file using scipy (no FFmpeg needed for WAV files).
        
        Args:
            audio_path: Path to WAV file
            
        Returns:
            Audio data as numpy array normalized for Whisper
        """
        from scipy.io import wavfile
        
        print(f"📂 Loading audio file: {audio_path}")
        
        # Read WAV file
        sample_rate, audio_data = wavfile.read(audio_path)
        
        # Convert to float32 and normalize
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0
        elif audio_data.dtype == np.float32:
            pass  # Already float32
        else:
            audio_data = audio_data.astype(np.float32)
        
        # Convert stereo to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Resample to 16kHz if needed (Whisper expects 16kHz)
        if sample_rate != 16000:
            from scipy import signal
            num_samples = int(len(audio_data) * 16000 / sample_rate)
            audio_data = signal.resample(audio_data, num_samples)
        
        print(f"✅ Audio loaded: {len(audio_data)/16000:.1f} seconds")
        return audio_data.astype(np.float32)
        
    def transcribe(
        self, 
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the audio file (WAV, MP3, etc.)
            language: Optional language code (e.g., 'en', 'es', 'hi')
                     If None, language is auto-detected
            task: 'transcribe' or 'translate' (translate to English)
            
        Returns:
            Dictionary containing:
                - text: Full transcription text
                - segments: List of segments with timestamps
                - language: Detected/specified language
                - duration: Audio duration in seconds
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        print(f"🎯 Transcribing: {audio_path}")
        
        # Prepare options
        options = {
            "task": task,
            "verbose": False
        }
        
        if language:
            options["language"] = language
        
        # Try to load WAV file directly with scipy (no FFmpeg needed)
        try:
            if audio_path.lower().endswith('.wav'):
                audio_data = self._load_audio_wav(audio_path)
                result = self.model.transcribe(audio_data, **options)
            else:
                # For non-WAV files, use Whisper's default loader (needs FFmpeg)
                result = self.model.transcribe(audio_path, **options)
        except Exception as e:
            print(f"⚠️ Error with scipy loader: {e}")
            print("Trying Whisper's built-in loader...")
            result = self.model.transcribe(audio_path, **options)
        
        # Process segments for easier access
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "id": segment.get("id"),
                "start": segment.get("start"),
                "end": segment.get("end"),
                "text": segment.get("text", "").strip()
            })
            
        transcription = {
            "text": result.get("text", "").strip(),
            "segments": segments,
            "language": result.get("language", "unknown"),
            "duration": segments[-1]["end"] if segments else 0
        }
        
        print(f"✅ Transcription complete! ({len(transcription['text'])} characters)")
        print(f"   Language detected: {transcription['language']}")
        print(f"   Duration: {transcription['duration']:.1f} seconds")
        
        return transcription
    
    def transcribe_and_save(
        self,
        audio_path: str,
        meeting_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio and save the result to a file.
        
        Args:
            audio_path: Path to the audio file
            meeting_name: Optional name for the meeting
            language: Optional language code
            
        Returns:
            Dictionary with transcription and saved file path
        """
        # Transcribe
        result = self.transcribe(audio_path, language)
        
        # Generate filename
        if meeting_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            meeting_name = f"transcript_{timestamp}"
            
        # Save as text file
        txt_path = TRANSCRIPTS_DIR / f"{meeting_name}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Meeting Transcript: {meeting_name}\n")
            f.write(f"Language: {result['language']}\n")
            f.write(f"Duration: {result['duration']:.1f} seconds\n")
            f.write("=" * 60 + "\n\n")
            f.write(result['text'])
            
        # Save as JSON (with segments)
        json_path = TRANSCRIPTS_DIR / f"{meeting_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        result['txt_path'] = str(txt_path)
        result['json_path'] = str(json_path)
        
        print(f"📄 Transcript saved: {txt_path}")
        
        return result
    
    def get_formatted_transcript(self, segments: List[Dict]) -> str:
        """
        Format transcript segments with timestamps.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Formatted transcript string with timestamps
        """
        lines = []
        for segment in segments:
            start = self._format_time(segment['start'])
            end = self._format_time(segment['end'])
            text = segment['text']
            lines.append(f"[{start} - {end}] {text}")
            
        return "\n".join(lines)
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def transcribe_file(audio_path: str, output_name: Optional[str] = None) -> str:
    """
    Convenience function to transcribe an audio file.
    
    Args:
        audio_path: Path to audio file
        output_name: Optional name for output files
        
    Returns:
        Transcribed text
    """
    transcriber = Transcriber()
    result = transcriber.transcribe_and_save(audio_path, output_name)
    return result['text']


def get_available_models() -> List[str]:
    """Get list of available Whisper model sizes."""
    return ["tiny", "base", "small", "medium", "large"]


if __name__ == "__main__":
    # Test transcription
    print("\n🎤 Whisper Transcription Module")
    print("=" * 40)
    print("\nAvailable models:", get_available_models())
    print(f"Current model: {WHISPER_MODEL}")
    
    # Check for test file
    test_files = list(Path("recordings").glob("*.wav"))
    if test_files:
        print(f"\nFound {len(test_files)} recording(s):")
        for f in test_files:
            print(f"  - {f.name}")
            
        print("\nTranscribing first file...")
        text = transcribe_file(str(test_files[0]))
        print("\n--- Transcription ---")
        print(text[:500] + "..." if len(text) > 500 else text)
    else:
        print("\nNo recordings found. Record a meeting first!")
