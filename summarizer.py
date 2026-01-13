"""
Google Meet Summarizer - Summarization Module
==============================================
Handles AI-powered meeting summarization using Google Gemini.
"""

import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import json

from config import GEMINI_API_KEY, GEMINI_MODEL, SUMMARIES_DIR, SUMMARY_PROMPT


class Summarizer:
    """
    Generates intelligent meeting summaries using Google Gemini AI.
    
    Extracts:
    - Key discussion points
    - Action items with assignees
    - Decisions made
    - Follow-up items
    
    Usage:
        summarizer = Summarizer()
        summary = summarizer.summarize(transcript_text)
        print(summary)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer with Gemini API.
        
        Args:
            api_key: Optional Gemini API key (uses config if not provided)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = None
        self._setup_api()
        
    def _setup_api(self) -> None:
        """Configure the Gemini API."""
        if not self.api_key or self.api_key == "your-gemini-api-key-here":
            print("⚠️  Warning: Gemini API key not configured!")
            print("   Get your free API key at: https://makersuite.google.com/app/apikey")
            print("   Set it in .env file or as GEMINI_API_KEY environment variable")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            print(f"✅ Gemini API configured successfully!")
        except Exception as e:
            print(f"❌ Failed to configure Gemini API: {e}")
            
    def is_configured(self) -> bool:
        """Check if the summarizer is properly configured."""
        return self.model is not None
    
    def summarize(
        self, 
        transcript: str, 
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a summary from meeting transcript.
        
        Args:
            transcript: The meeting transcript text
            custom_prompt: Optional custom prompt template
            
        Returns:
            Generated summary text
        """
        if not self.is_configured():
            return self._get_offline_summary(transcript)
            
        # Use custom prompt or default
        prompt_template = custom_prompt or SUMMARY_PROMPT
        prompt = prompt_template.format(transcript=transcript)
        
        try:
            print("🤖 Generating summary with Gemini AI...")
            response = self.model.generate_content(prompt)
            summary = response.text
            print("✅ Summary generated successfully!")
            return summary
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self._get_offline_summary(transcript)
    
    def _get_offline_summary(self, transcript: str) -> str:
        """
        Generate a basic offline summary when API is unavailable.
        
        This is a fallback that provides basic text analysis.
        """
        print("📝 Generating basic offline summary...")
        
        # Basic word count and statistics
        words = transcript.split()
        word_count = len(words)
        sentences = transcript.replace('!', '.').replace('?', '.').split('.')
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Extract potential action items (sentences with action words)
        action_words = ['will', 'should', 'must', 'need to', 'have to', 'going to', 
                       'action', 'task', 'deadline', 'complete', 'finish', 'do']
        potential_actions = []
        for sentence in sentences:
            if any(word in sentence.lower() for word in action_words):
                if len(sentence.strip()) > 10:
                    potential_actions.append(sentence.strip())
        
        # Generate basic summary
        summary = f"""
## 📋 Meeting Summary (Offline Mode)

> **Note**: This is a basic summary generated offline. For AI-powered summaries, 
> please configure your Gemini API key.

### 📊 Statistics
- **Word Count**: {word_count:,}
- **Sentences**: {sentence_count}
- **Estimated Duration**: {word_count // 150} minutes (based on avg. speaking rate)

### 📝 Full Transcript
{transcript[:1000]}{'...' if len(transcript) > 1000 else ''}

### ✅ Potential Action Items
{chr(10).join(['- [ ] ' + action[:100] for action in potential_actions[:5]]) or '- No action items detected'}

---
**To get better summaries, configure your Gemini API key!**
"""
        return summary
    
    def summarize_and_save(
        self,
        transcript: str,
        meeting_name: Optional[str] = None
    ) -> Dict:
        """
        Generate summary and save to file.
        
        Args:
            transcript: Meeting transcript text
            meeting_name: Optional name for the meeting
            
        Returns:
            Dictionary with summary and file path
        """
        # Generate summary
        summary = self.summarize(transcript)
        
        # Generate filename
        if meeting_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            meeting_name = f"summary_{timestamp}"
            
        # Save as markdown
        md_path = SUMMARIES_DIR / f"{meeting_name}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Meeting Summary: {meeting_name}\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(summary)
            
        print(f"📄 Summary saved: {md_path}")
        
        return {
            "summary": summary,
            "file_path": str(md_path),
            "meeting_name": meeting_name
        }
    
    def quick_summary(self, transcript: str, max_points: int = 5) -> str:
        """
        Generate a quick, condensed summary.
        
        Args:
            transcript: Meeting transcript
            max_points: Maximum number of key points
            
        Returns:
            Quick summary text
        """
        if not self.is_configured():
            return "Quick summary unavailable - API not configured"
            
        prompt = f"""
        Provide a very brief summary of this meeting in exactly {max_points} bullet points.
        Focus only on the most critical information.
        
        Transcript:
        {transcript}
        
        Format:
        • Point 1
        • Point 2
        ...
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Quick summary failed: {e}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def summarize_transcript_file(transcript_path: str) -> str:
    """
    Summarize a transcript from a file.
    
    Args:
        transcript_path: Path to transcript text file
        
    Returns:
        Generated summary
    """
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
        
    summarizer = Summarizer()
    return summarizer.summarize(transcript)


def check_api_status() -> bool:
    """Check if the Gemini API is working."""
    summarizer = Summarizer()
    
    if not summarizer.is_configured():
        print("❌ API not configured")
        return False
        
    try:
        response = summarizer.model.generate_content("Say 'API is working!'")
        print(f"✅ API Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🤖 Meeting Summarizer Module")
    print("=" * 40)
    
    # Check API status
    print("\nChecking Gemini API status...")
    api_ok = check_api_status()
    
    if not api_ok:
        print("\n💡 To configure the API:")
        print("   1. Get a free API key at: https://makersuite.google.com/app/apikey")
        print("   2. Create a .env file with: GEMINI_API_KEY=your-key-here")
        print("   3. Or set environment variable: set GEMINI_API_KEY=your-key-here")
    
    # Test with sample transcript
    sample = """
    John: Let's discuss the Q1 roadmap. We need to finalize the features.
    Sarah: I think we should prioritize the mobile app redesign.
    John: Agreed. Sarah, can you lead that? We need it done by March.
    Sarah: Yes, I'll create a project plan by next week.
    Mike: What about the API performance issues?
    John: Good point. Mike, can you investigate and report back?
    Mike: Sure, I'll have an analysis ready by Friday.
    John: Great. Let's reconvene next Tuesday to review progress.
    """
    
    print("\n📝 Testing with sample transcript...")
    summarizer = Summarizer()
    summary = summarizer.summarize(sample)
    print("\n--- Summary ---")
    print(summary)
