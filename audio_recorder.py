"""
Google Meet Summarizer - Audio Recorder Module
===============================================
Handles system audio capture for recording Google Meet sessions.
"""

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import threading
import queue

from config import RECORDINGS_DIR, SAMPLE_RATE, CHANNELS, DTYPE


class AudioRecorder:
    """
    Records system audio for Google Meet sessions.
    
    Usage:
        recorder = AudioRecorder()
        recorder.start_recording()
        # ... meeting happens ...
        filepath = recorder.stop_recording()
    """
    
    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS):
        """
        Initialize the audio recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)
            channels: Number of audio channels (default: 2 for stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread: Optional[threading.Thread] = None
        self.current_device: Optional[int] = None
        
    def get_audio_devices(self) -> List[Dict]:
        """
        Get list of available audio input devices.
        
        Returns:
            List of dictionaries containing device info
        """
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
                
        return input_devices
    
    def get_default_device(self) -> Optional[int]:
        """Get the default input device ID."""
        try:
            return sd.default.device[0]
        except:
            return None
    
    def set_device(self, device_id: int) -> None:
        """
        Set the audio input device to use for recording.
        
        Args:
            device_id: The device ID from get_audio_devices()
        """
        self.current_device = device_id
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())
        
    def _recording_worker(self):
        """Worker thread that handles audio recording."""
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=DTYPE,
                device=self.current_device,
                callback=self._audio_callback
            ):
                while self.is_recording:
                    sd.sleep(100)  # Sleep for 100ms
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_recording = False
    
    def start_recording(self, device_id: Optional[int] = None) -> bool:
        """
        Start recording audio.
        
        Args:
            device_id: Optional device ID to use (uses default if not specified)
            
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            print("Already recording!")
            return False
            
        # Set device if specified
        if device_id is not None:
            self.current_device = device_id
            
        # Clear the queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        # Start recording
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.start()
        
        print("🎤 Recording started...")
        return True
    
    def stop_recording(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Stop recording and save the audio file.
        
        Args:
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the saved audio file, or None if recording failed
        """
        if not self.is_recording:
            print("Not currently recording!")
            return None
            
        # Stop recording
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
            
        # Collect all audio data from queue
        audio_chunks = []
        while not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get_nowait()
                audio_chunks.append(chunk)
            except queue.Empty:
                break
                
        if not audio_chunks:
            print("No audio data recorded!")
            return None
            
        # Concatenate audio chunks
        audio_data = np.concatenate(audio_chunks, axis=0)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{timestamp}"
            
        # Save audio file
        filepath = RECORDINGS_DIR / f"{filename}.wav"
        write(str(filepath), self.sample_rate, audio_data)
        
        print(f"✅ Recording saved: {filepath}")
        return str(filepath)
    
    def get_recording_duration(self) -> float:
        """
        Get the current recording duration in seconds.
        
        Returns:
            Duration in seconds
        """
        if not self.is_recording:
            return 0.0
            
        # Estimate based on queue size (approximate)
        return self.audio_queue.qsize() * 0.1  # Each chunk is ~100ms
    
    def is_currently_recording(self) -> bool:
        """Check if currently recording."""
        return self.is_recording


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def list_audio_devices():
    """Print all available audio devices."""
    print("\n🎧 Available Audio Devices:")
    print("=" * 60)
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        device_type = []
        if device['max_input_channels'] > 0:
            device_type.append("INPUT")
        if device['max_output_channels'] > 0:
            device_type.append("OUTPUT")
            
        print(f"[{i}] {device['name']}")
        print(f"    Type: {', '.join(device_type)}")
        print(f"    Channels: In={device['max_input_channels']}, Out={device['max_output_channels']}")
        print()


def test_recording(duration: int = 5):
    """
    Test recording for a specified duration.
    
    Args:
        duration: Recording duration in seconds
    """
    print(f"\n🎤 Testing recording for {duration} seconds...")
    
    recorder = AudioRecorder()
    recorder.start_recording()
    
    import time
    time.sleep(duration)
    
    filepath = recorder.stop_recording("test_recording")
    
    if filepath:
        print(f"✅ Test recording saved to: {filepath}")
    else:
        print("❌ Test recording failed!")


if __name__ == "__main__":
    # List devices and test recording
    list_audio_devices()
    
    print("\nWould you like to test recording? (y/n): ", end="")
    if input().lower() == 'y':
        test_recording(5)
