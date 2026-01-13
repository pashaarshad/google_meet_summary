# 🚀 Deployment Guide - Google Meet Summarizer

This guide covers multiple deployment options for your Google Meet Summarizer application.

---

## ⚠️ Important Note

**This app requires system audio access**, which means it works best when run **locally** on your computer. Cloud deployments (Streamlit Cloud, Heroku, etc.) cannot access your system audio or microphone for Google Meet.

**Recommended approach**: Run locally during meetings, or use as a desktop application.

---

## Option 1: Run Locally (Recommended)

### Prerequisites
- Python 3.8+
- Gemini API Key

### Steps

```powershell
# 1. Navigate to project folder
cd C:\Users\Admin\Desktop\CodePlay\google_meet_summary

# 2. Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
# Create .env file with:
# GEMINI_API_KEY=your-key-here

# 5. Run the app
python -m streamlit run app.py
```

The app will be available at: **http://localhost:8501**

---

## Option 2: Create a Desktop Shortcut

### Windows Batch Script

Create `start_app.bat` in your project folder:

```batch
@echo off
cd /d "C:\Users\Admin\Desktop\CodePlay\google_meet_summary"
python -m streamlit run app.py
pause
```

Double-click this file to start the app!

---

## Option 3: Deploy to Streamlit Cloud (For Demo Only)

> ⚠️ **Note**: Audio recording won't work on cloud. This is for showcasing the UI only.

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/google-meet-summarizer.git
   git push -u origin main
   ```

2. **Create `secrets.toml`** for Streamlit Cloud
   - Go to Streamlit Cloud settings
   - Add secret: `GEMINI_API_KEY = "your-key-here"`

3. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Deploy!

---

## Option 4: Package as Executable (PyInstaller)

Turn your app into a standalone `.exe` file:

```powershell
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed app.py
```

The executable will be in the `dist/` folder.

---

## Option 5: Docker Container

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
docker build -t google-meet-summarizer .
docker run -p 8501:8501 -e GEMINI_API_KEY=your-key google-meet-summarizer
```

---

## Option 6: Deploy to Your Own Server

### Requirements
- Linux server (Ubuntu recommended)
- Python 3.8+
- Domain name (optional)

### Steps

```bash
# 1. SSH into your server
ssh user@your-server-ip

# 2. Clone your repo
git clone https://github.com/YOUR_USERNAME/google-meet-summarizer.git
cd google-meet-summarizer

# 3. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Create .env file
echo "GEMINI_API_KEY=your-key-here" > .env

# 5. Run with nohup (keeps running after logout)
nohup streamlit run app.py --server.port=8501 &

# 6. (Optional) Set up Nginx reverse proxy for HTTPS
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Port already in use | Use `--server.port=8502` |
| Can't access externally | Add `--server.address=0.0.0.0` |
| Audio not working | Must run locally for audio features |
| Slow transcription | Use smaller Whisper model in config.py |

---

## Recommended: Local + Startup Script

For the best experience, create a startup script that runs when you need to summarize meetings:

### `start_summarizer.ps1` (PowerShell)

```powershell
# Start Google Meet Summarizer
Write-Host "🎤 Starting Google Meet Summarizer..." -ForegroundColor Cyan

# Navigate to project
Set-Location "C:\Users\Admin\Desktop\CodePlay\google_meet_summary"

# Activate virtual environment (if using)
# .\venv\Scripts\Activate

# Start the app
Start-Process "http://localhost:8501"
python -m streamlit run app.py
```

---

## Credits

**Created by Arshad Pasha**  
🌐 [arshadpasha.tech](https://arshadpasha.tech)

---

*Made with ❤️ for better meetings*
